#!/usr/bin/env python
"""
recases words, referring to the original (tagged) string to identify proper nouns.
expects the input file to be POS tagged
"""

import sys
import re

alnum = re.compile(r'[0-9a-zA-Z]')

if len(sys.argv != 3):
    print 'python scripts/recase.py input-file.pos candidate-file.txt'
    sys.exit()

with open(sys.argv[1]) as origfile, open(sys.argv[2]) as genfile:

    # compare tokens in each line
    for origline, genline in zip(origfile, genfile):
        otaggedtoks = [o.rsplit('_', 1) for o in origline.split()]
        otoks = [o[0] for o in otaggedtoks]
        opos = [o[1] for o in otaggedtoks]
        gtoks = genline.split()

        # identify the first alphanumeric token in original string, which
        # will always be capitalized (if alpha)
        first_word = 0
        for i, o in enumerate(otoks):
            if alnum.match(o[0]):
                first_word = i
                break

        # keep track of capitalized tokens in the original text
        captoks = {}

        # capitalize proper nouns
        # do not capitalize other words since they may have been wrong
        for i, tok in enumerate(otoks):
            if opos[i].startswith('NNP'):
                captoks[tok.lower()] = tok

        # capitalize first alphanum word in candidate
        first_word = 0
        for i, g in enumerate(gtoks):
            if alnum.match(g[0]):
                first_word = i
                break

        # capitalize i or words capitalized in the input
        gcased = []
        for i, g in enumerate(gtoks):
            if g == 'i':
                gcased.append('I')
            elif i == first_word:
                gcased.append(g.capitalize())
            else:
                gcased.append(captoks.get(g, g))

        print ' '.join(gcased)
