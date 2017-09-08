#!/usr/bin/env python

"""
Checks speling of every word and, if not in the dictionary, creates rules with spelling suggestions
Some notes:
- handles both parsed and unparsed input
- capitalization matters! will return lc rules by default; use flag --mixed to preserve case
- suggestions for properly spelled words can be noisy (e.g. "will"), so by default only makes
  suggestions for misspelled words. use flag --suggest to include correctly spelled words
"""
import argparse
import kenlm
import sys
import math
import codecs
import enchant
import re
from nltk.tree import Tree


def get_tokens(line, parsed):
    """getlist of (tok, pos) tuples. if not parsed, returns (tok, X)"""
    if parsed:
        return Tree.fromstring(line).pos()
    else:
        toks = line.split()
        return zip(toks, ['X'] * len(toks))

def get_features(pos, tok, newtok):
    """get joshua-formatted features for a spelling rule"""
    return ' '.join(['CharCountDiff=%d' % (len(newtok) - len(tok)),
                     'Lexical=1',
                     'SourceWords=1',
                     'TargetWords=%d' % len(newtok.split()),
                     'WordCountDiff=%d' % (len(newtok.split()) - len(tok.split())),
                     'CharLogCR=%f' % math.log(1. * len(newtok) / len(tok)),
                     'mispelled=%f' % ((1 - get_weight(tok)) if use_lm else 1),
                     'alternate-spelling=%f' % (0 if tok == newtok else get_weight(newtok)),
                     'Identity=%d' % (1 if tok == newtok else 0),
                     'is-nnp=%d' % (1 if pos.startswith('NNP') else 0)])


def get_weight(tok):
    score = lm.score(tok)/len(tok.split())
    if score == unk:
        return 0
    return math.exp(score)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--suggest', action='store_true',
                        help='suggest alternate spellings for words in dictionary')
    parser.add_argument('--mixed', action='store_true', help='use mixed case (default: lower case)')
    parser.add_argument('--lm', required=True,
                        help='path to language model')
    parser.add_argument('--prefix', required=True,
                        help='prefix of corpus (like data/corpus/CORPUSNAME)')
    args = parser.parse_args()

    d = enchant.Dict('en')
    wordp = re.compile('^[a-zA-Z][a-zA-Z-]*$')
    parsed = False
    generated = set()
    print >>sys.stderr, 'Loading lm'
    lm = kenlm.Model(args.lm)
    unk = lm.score('<unk>', bos=False, eos=False)
    print >>sys.stderr, 'done'

    with codecs.open(args.prefix + '.tok.err', 'r', 'utf-8') as fin:
        for i, line in enumerate(fin):
            line = line.strip()
            if len(line) == 0:
                continue
            if not parsed:
                parsed = (line[0] == '(' and line[-1] == ')')
            for tok, pos in get_tokens(line, parsed):
                key = tok + ' ' + pos
                # skip words we've already seen or non-word tokens
                if key in generated or not wordp.match(tok):
                    continue
                if d.check(tok) and not args.suggest():
                    continue
                generated.add(key)
                if '-' in tok:
                    # enchant is bad with hyphenated words
                    # first, check if the unhyphenated word is in the dict
                    # if it isn't and the hyphenated parts are correctly spelled, skip it
                    if d.check(tok.replace('-', '')):
                        pass
                    elif all([False if len(part) == 0 else d.check(part) for part in tok.split('-')]):
                        continue
                newtoks = d.suggest(tok)
                if not args.mixed:
                    newtoks = set([t.lower() for t in newtoks])
                    tok = tok.lower()
                for newtok in newtoks:
                    if "'" in newtok:
                        continue
                    print(' ||| '.join(['[%s]' % pos,
                                        tok,
                                        newtok,
                                        get_features(pos, tok, newtok),
                                        '0-0']))

    sys.stderr.write('Generated spelling alterates for %d words\n' % len(generated))
