#!/usr/bin/env python
"""
adds various features related to grammatical errors to a grammar formatted
X ||| LHS ||| RHS ||| FEATURES ||| ALIGNMENT

Usage: zcat grammar.gz | python scripts/lib/add_error_features.py | gzip -9 > grammar.gec-features.gz
"""

import sys
import math
import os
import enchant
import inflect
import kenlm
import argparse
import pickle
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.metrics.distance import edit_distance


class FeatureCalculator:
    def __init__(self):
        self.WN_TAGS = {'J': 'a', 'N': 'n', 'R': 'r', 'V': 'v'}
        self.wnl = WordNetLemmatizer()
        self.dictionary = enchant.Dict('en')
        self.inflengine = inflect.engine()

    def load_lm(self, lmpath):
        """load language model (for scoring spelling changes)"""
        print >>sys.stderr, 'Loading lm'
        self.lm = kenlm.Model(lmpath)
        self.unk = self.lm.score('<unk>', bos=False, eos=False)
        print >>sys.stderr, 'done\n'

    def get_weight(self, tok):
        """get lm prob of spelling suggestions"""
        score = self.lm.score(tok, bos=False, eos=False)/len(tok.split())
        if score == self.unk:
            return 0
        return math.exp(score)

    """
    sample rules:
    [X] ||| 000 [X,1] is nearly ||| [X,1] is nearly ||| <<features>> ||| 2-1 3-2
    [X] ||| 000 [X,1] is nearly twice ||| [X,1] is nearly twice ||| <<features>> ||| 2-1 3-2 4-3
    """
    def load_tagged_vocab(self, storepath='store'):
        """
        load pos tagged and morpha analyzed vocab list. the first time run, generates a lookup
        dict from store/vocab and store/vocab.morph text files. subsequent runs, will load pickle
        directly.
        """
        self.lookup_table = {}
        self.lookup_updated = False
        if not os.path.exists(storepath):
            os.path.makedirs(storepath)

        sys.stderr.write('Loading analyzed words...\n')
        # load from pickle if exists
        if os.path.exists(os.path.join(storepath, 'vocab_lookup.pkl')):
            self.lookup_table = pickle.load(open(os.path.join(storepath, 'vocab_lookup.pkl'), 'rb'))
        # create from text files if they exist
        elif os.path.exists(os.path.join(storepath, 'vocab')) and \
             os.path.exists(os.path.join(storepath, 'vocab.morpha')):
            self.lookup_updated = True
            for orig, tagged in zip(open(os.path.join(storepath, 'vocab')),
                                    open(os.path.join(storepath, 'vocab.morpha'))):
                if ' ' in tagged:
                    continue
                tok, tag = tagged.strip().rsplit('_', 1)
                self.lookup_table[orig.strip().lower()] = [tok.lower().split('+'), tag]
        sys.stderr.write('Done\n')
        return self.lookup_table

    def get_pos(self, tok):
        """get pos tag of a token"""
        if tok not in self.lookup_table:
            _tok, pos = pos_tag([tok])[0]
            self.lookup_table[tok] = [None, pos]
            self.lookup_updated = True
        return tok, self.lookup_table[tok][1].upper()

    def dump_tagged_vocab(self, storepath='store'):
        """pickle updated lookup table"""
        if self.lookup_updated:
            sys.stderr.write('Dumping updated lookup table to %s/vocab_lookup.pkl\n' % storepath)
            pickle.dump(self.lookup_table, open(os.path.join(storepath, 'vocab_lookup.pkl', 'wb')))

    def increment(self, features, fname, v=1):
        """increase value of fname in features (create if isn't there)"""
        if fname not in features:
            features[fname] = 0
        features[fname] += v

    def get_morphology(self, tok):
        """if N or V, returns morpha analysis else returns WN lemma"""
        if self.lookup_table[tok][0] is None:
            self.lookup_updated = True
            wntag = self.WN_TAGS.get(self.lookup_table[tok][1])
            if wntag:
                self.lookup_table[tok][0] = [self.wnl.lemmatize(tok, wntag)]
            else:
                self.lookup_table[tok][0] = [tok]
        return self.lookup_table[tok][0]

    def analyze_unaligned(self, foundlist, toks):
        """get pos tags for unaligned tokens"""
        for ind, found in enumerate(foundlist):
            if not found:
                _, pos = self.get_pos(toks[ind])
                yield pos

    def get_features(self, lhs, rhs, alignment=['0-0']):
        """calculate and return features for a rule"""
        features = {}
        # no changes
        if lhs == rhs:
            return features

        # indicate if tokens are aligned
        rfound = [(rtok[0] == '[') for rtok in rhs]
        lfound = [(ltok[0] == '[') for ltok in lhs]

        # iterate through aligned tokens--assume no NTs
        for tuple in alignment:
            lind, rind = [int(i) for i in tuple.split('-')]
            lfound[lind] = True
            rfound[rind] = True
            if lhs[lind] == rhs[rind]:
                continue

            # calculate features for substituion
            self.increment(features, 'substituted')
            self.increment(features, 'char-ld', edit_distance(lhs[lind], rhs[rind]))
            if rhs[rind] in self.dictionary.suggest(lhs[lind]):
                if self.dictionary.check(lhs[lind]):
                    self.increment(features, 'alternate-spelling',
                                   v=self.get_weight(rhs[rind]))
                else:
                    self.increment(features, 'mispelled',
                                   v=self.get_weight(rhs[rind]))
            # if the tokens aren't the same, compare them
            ltok, lpos = self.get_pos(lhs[lind])
            rtok, rpos = self.get_pos(rhs[rind])
            self.increment(features, '%s-%s' % (lpos, rpos))
            if rpos[0] == 'W' or rpos[0] == 'C':
                self.increment(features, '%s-error' % (rpos[:2]))
            else:
                self.increment(features, '%s-error' % (rpos[0]))
            # compare lemmas/morphology
            if self.do_morph:
                try:
                    lmorph = self.get_morphology(ltok)
                    rmorph = self.get_morphology(rtok)

                    if lmorph[0] != rmorph[0]:
                        if len(lmorph) + len(rmorph) > 2:
                            self.increment(features, 'diff-lemma-diff-morph')
                        else:
                            self.increment(features, 'diff-lemma-same-morph')
                    else:
                        self.increment(features, 'same-lemma-diff-morph')
                    if len(lmorph) + len(rmorph) > 2:
                        self.increment(features,
                                       'morph-%s-%s' % ('+'.join(lmorph[1:]), '+'.join(rmorph[1:])))
                except:
                    sys.stderr.write('Error handling morphology in rule %d\n' % i)

        # calculate feaures for deletion
        for deltok in self.analyze_unaligned(lfound, lhs):
            self.increment(features, 'deleted')
            self.increment(features, deltok + '-')
        # calculate feaures for insertion
        for instok in self.analyze_unaligned(rfound, rhs):
            self.increment(features, 'inserted')
            self.increment(features, '-' + instok)

        self.increment(features, 'tok-ld', edit_distance(lhs, rhs))
        return features

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='zcat grammar.gz | python scripts/lib/add_error_features --lm path/to/lm | gzip -9 > grammar.gec-features.gz')
    parser.add_argument('--lm', required=True,
                        help='path to language model')
    parser.add_argument('--store', help='directory containing morpha lookup table (created with sctipts/generate_morpha_lookup.sh)')

    args = parser.parse_args()

    fcalc = FeatureCalculator()
    fcalc.load_lm(args.lm)
    fcalc.load_tagged_vocab(args.store)
    for i, line in enumerate(sys.stdin):
        category, _lhs, _rhs, _features, _alignment = [s.strip() for s in line.split(' ||| ')]
        lhs = _lhs.split()
        rhs = _rhs.split()
        alignment = _alignment.split()
        features = {k: v for k, v in [ff.split('=') for ff in _features.split()]}
        features.pop('alternate-spelling', None)
        features.pop('mispelled', None)
        features.update(fcalc.get_features(lhs, rhs, alignment))

        print(' ||| '.join([category, _lhs, _rhs, ' '.join(
            ['%s=%s' % (k, v) for k, v in features.items()]), _alignment]))
    fcalc.dump_tagged_vocab(args.store)
