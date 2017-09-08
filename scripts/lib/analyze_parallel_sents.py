#!/usr/bin/env python3
"""
compares two aligned strings and prints out feature calculations
input format:
LHS+morph_POS ||| RHS+morph_POS ||| alignment ||| RAW LHS ||| RAW RHS
"""

import time
import sys
import math
import enchant
import kenlm
from nltk.stem import WordNetLemmatizer
from nltk.metrics.distance import edit_distance

SKIP = {'WordCountDiff', 'CharCountDiff', 'spell-change', 'spell-correction', 'Count'}


class FeatureCalculator:

    def __init__(self):
        self.WN_TAGS = {'J': 'a', 'N': 'n', 'R': 'r', 'V': 'v'}
        self.wnl = WordNetLemmatizer()
        self.dictionary = enchant.Dict('en')
        self.lookup_table = {}

    def load_lm(self, lmpath):
        """load language model (for scoring spelling changes)"""
        print >>sys.stderr, 'Loading lm...'
        self.lm = kenlm.Model(lmpath)
        self.unk = self.lm.score('<unk>', bos=False, eos=False)
        print >>sys.stderr, 'done'

    def get_weight(self, tok):
        """get lm prob of spelling suggestions"""
        score = self.lm.score(tok, bos=False, eos=False)/len(tok.split())
        if score == self.unk:
            return 0
        return math.exp(score)

    def increment(self, features, fname, v=1):
        """increase value of fname  in features (create if isn't there)"""
        if fname not in features:
            features[fname] = 0
        features[fname] += v

    def get_morphology(self, tok, pos, morph):
        """
        if N or V, returns morpha analysis else returns WN lemma
        return format is (lemma, morph)
        """
        if pos[0] == 'N' or pos[0] == 'V':
            if morph:
                return [tok, morph]
            return [tok]
        key = tok + '_' + pos
        if key not in self.lookup_table:
            wntag = self.WN_TAGS.get(pos[0])
            if wntag:
                self.lookup_table[key] = [self.wnl.lemmatize(tok, wntag)]
            else:
                self.lookup_table[key] = [tok]
        return self.lookup_table[key]

    def analyze_unaligned(self, foundlist, toks):
        for ind, found in enumerate(foundlist):
            if not found:
                tok, pos, morph = self.get_tok_morph_pos(toks[ind])
                yield pos

    def get_tok_morph_pos(self, s):
        _tok, pos = s.rsplit('_', 1)
        _morph = _tok.rsplit('+', 1)
        tok = _morph[0]
        morph = '' if len(_morph) == 1 else _morph[1]
        return tok, pos, morph

    def get_features(self, lhs, rhs, alignment=['0-0']):
        features = {}
        if lhs == rhs:
            return features
        rfound = [False for _ in rhs]
        lfound = [False for _ in lhs]

        # iterate through aligned tokens--assume no NTs
        for tuple in alignment:
            lind, rind = [int(i) for i in tuple.split('-')]
            lfound[lind] = True
            rfound[rind] = True
            if lhs[lind] == rhs[rind]:
                self.increment(features, 'identical')
                continue
            ltok, lpos, lmorph = self.get_tok_morph_pos(lhs[lind])
            rtok, rpos, rmorph = self.get_tok_morph_pos(rhs[rind])

            self.increment(features, 'substituted')
            self.increment(features, 'char-ld', edit_distance(ltok, rtok))
            if rtok in self.dictionary.suggest(ltok):
                self.increment(features, 'spelling')
                if self.dictionary.check(ltok):
                    self.increment(features, 'alternate-spelling')
                                   # v=self.get_weight(rtok))
                else:
                    self.increment(features, 'mispelled')
                                   # v=self.get_weight(rtok))

            self.increment(features, '%s-%s' % (lpos, rpos))
            if rpos[0] == 'W' or rpos[0] == 'C':
                self.increment(features, '%s-error' % (rpos[:2]))
            else:
                self.increment(features, '%s-error' % (rpos[0]))

            # compare lemmas/morphology
            lmorphsplit = self.get_morphology(ltok, lpos, lmorph)
            rmorphsplit = self.get_morphology(rtok, rpos, rmorph)

            if lmorphsplit[0] != rmorphsplit[0]:
                if len(lmorphsplit) + len(rmorphsplit) > 2:
                    self.increment(features, 'diff-lemma-diff-morph')
                else:
                    self.increment(features, 'diff-lemma-same-morph')
            else:
                self.increment(features, 'same-lemma-diff-morph')

        for deltok in self.analyze_unaligned(lfound, lhs):
            self.increment(features, 'deleted')
            self.increment(features, deltok + '-')
        for instok in self.analyze_unaligned(rfound, rhs):
            self.increment(features, 'inserted')
            self.increment(features, '-' + instok)

        return features

if __name__ == '__main__':
    if len(sys.argv != 2 or '-h' in sys.argv):
        print 'cat input | python scripts/lib/analyze_parallel_sents.py'
        print '  Input should be formatted LHS+morph_POS ||| RHS+morph_POS ||| alignment ||| RAW LHS ||| RAW RHS'
        print '  Use scripts/compare_edits.sh, which handles preparing the input'
        exit
    fcalc = FeatureCalculator()
    fcalc.load_lm(sys.argv[1])
    totals = {}
    count = 0
    for i, line in enumerate(sys.stdin):
        count += 1
        _lhs_anno, _rhs_anno, _alignment, lhs_raw, rhs_raw = [s.strip() for s in line.split(' ||| ')]
        lhs = _lhs_anno.split()
        rhs = _rhs_anno.split()
        alignment = _alignment.split()
        features = fcalc.get_features(lhs, rhs, alignment)
        features['tok-ld'] = edit_distance(lhs_raw.split(), rhs_raw.split())
        features['lm-diff'] = fcalc.lm.score(rhs_raw) / fcalc.lm.score(lhs_raw)
        ret = []
        for k, v in features.items():
            totals[k] = totals.get(k, 0) + v
            ret.append('%s=%s' % (k, str(v)))
        print(' '.join(ret))
    print('=' * 80)
    print('TOTAL: ' + ' '.join(['%s=%s' % (k, str(v)) for k, v in totals.items()]))
    print('MEAN: ' + ' '.join(['%s=%s' % (k, str(1.*v/count)) for k, v in totals.items()]))
