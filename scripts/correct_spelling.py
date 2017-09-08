#!/usr/bin/env python

"""
this script corrects the spelling by choosing the word suggested
by enchant with the greatest likelihood (out of context)
"""

import kenlm
import sys
import math

from enchant.checker import SpellChecker


def load_lm(lmpath):
    return kenlm.Model(lmpath)


def get_weight(tok):
    score = lm.score(tok, bos=False, eos=False)/len(tok.split())
    if score == unk:
        return 0
    return math.exp(score)


if __name__ == '__main__':
    if '-h' in sys.argv or len(sys.argv) != 2:
        print 'cat text | python scripts/correct_spelling.py path/to/lm'
        sys.exit()

    # load LM
    print >>sys.stderr, 'Loading lm'
    lm = load_lm(sys.argv[1])
    unk = lm.score('<unk>', bos=False, eos=False)
    print >>sys.stderr, 'done'

    # check each line
    for line in sys.stdin:
        chkr = SpellChecker('en', line.strip())
        # for each error, replace with the suggestion with the highest ll
        for err in chkr:
            best_option = None
            best_score = float('-inf')
            for sug in err.suggest():
                score = get_weight(sug)
                if score > best_score:
                    best_score = score
                    best_option = sug
            if best_option is not None:
                err.replace(best_option)
        print chkr.get_text()
