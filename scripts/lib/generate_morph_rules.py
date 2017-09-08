#!/usr/bin/env python
"""
generates new features with morphological variants
must have already called generate_morpha_lookup.sh
"""
import re
import sys
import os
import math
import morphg
import enchant
from add_error_features import FeatureCalculator

SUFFIXES = {'V': ['ed', 'ing', 'en', 's', ''],
            'N': ['s', '']}


def get_features(tok, newtok):
    """calculate sentence-level features"""
    print >>sys.stderr, tok, newtok, len(tok), len(newtok)
    return ' '.join(['CharCountDiff=%d' % (len(newtok) - len(tok)),
                     'Lexical=1',
                     'SourceWords=1',
                     'TargetWords=%d' % len(newtok.split()),
                     'WordCountDiff=%d' % (len(newtok.split()) - len(tok.split())),
                     'CharLogCR=%f' % math.log(1. * len(newtok) / max(1, len(tok))),
                     'Identity=%d' % (1 if tok == newtok else 0),
                     'gen-morph=1'])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: scripts/lib/generate_morph_rules.py store/vocab'
        sys.exit()

    d = enchant.Dict('en')
    wordp = re.compile('^[a-zA-Z][a-zA-Z-]*$')
    morphg.open_pipe()
    fcalc = FeatureCalculator()
    fcalc.load_tagged_vocab()

    to_generate = {}
    with open('morphg-in.tmp', 'w') as fout:
        for tok, tagged in zip(open(sys.argv[1]), open(sys.argv[1] + '.morpha')):
            if ' ' in tagged:
                continue
            if not wordp.match(tok):
                continue
            # for all input words, generate morphological variants if it is a N or V in the dict
            tok = tok.strip()
            if not d.check(tok):
                continue
            morph, pos = tagged.strip().rsplit('_', 1)
            # only do noun/verbs
            if pos[0] not in 'NV':
                continue
            key = (tok + '_' + pos).lower()
            # already generated, so pass
            if key in to_generate:
                continue
            to_generate[key] = []
            morph = morph.split('+')
            lemma = morph[0]
            suffix = '' if len(morph) == 1 else morph[1]
            # create all possible rules
            for _suffix in SUFFIXES[pos[0]]:
                if _suffix == suffix:
                    continue
                if _suffix == '':
                    newtok = lemma
                else:
                    morphin = lemma + '+' + _suffix + '_' + pos[0]
                    to_generate[key].append(morphin)
                    fout.write(morphin + '\n')
                    continue
    os.system('sh scripts/lib/call_morphg.sh morphg-in.tmp')
    generated = {}
    for orig, mg in zip(open('morphg-in.tmp'), open('morphg-in.tmp.out')):
        generated[orig.strip()] = mg.strip()

    for k, morphs in to_generate.items():
        tok, pos = k.rsplit('_', 1)
        for morph in morphs:
            if morph not in generated:
                print >>sys.stderr, 'Error:', morph, 'missing'
                continue
            if not d.check(generated[morph]):
                print >>sys.stderr, 'Error:', morph, generated[morph], 'not in dict'
                continue

            print ' ||| '.join(['[X]', tok, generated[morph],
                                get_features(tok, generated[morph]),
                                '0-0'])
