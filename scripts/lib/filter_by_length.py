#!/usr/bin/env python
""" skips lines with 100 or more tokens or where one side has 9x or more the length of the other"""
import sys
import codecs

with codecs.open(sys.argv[1] + '.err', 'r', 'utf-8') as fin1, \
     codecs.open(sys.argv[1] + '.corr', 'r', 'utf-8') as fin2, \
     codecs.open(sys.argv[1] + '.filtered.err', 'w', 'utf-8') as fout1, \
     codecs.open(sys.argv[1] + '.filtered.corr', 'w', 'utf-8') as fout2:
    for l1, l2 in zip(fin1, fin2):
        len1 = len(l1.split())
        len2 = len(l2.split())
        if len1 * len2 == 0:
            continue
        if len1 < 100 and len2 < 100:
            if len1 / len2 < 9 and len2 / len1 < 9:
                fout1.write(l1)
                fout2.write(l2)
