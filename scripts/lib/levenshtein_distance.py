#!/usr/bin/env python
"""
calculautes the levenshtein distance between each line of parallel text
input can be std in (separated by tab) or two file paths
"""

import sys
from nltk.metrics.distance import edit_distance

if '-h' in sys.argv:
    print "python scripts/lib/levenshtein_distance.py file1 file2"
    print "paste file1 file2 | python scripts/lib/levenshtein_distance.py"
    sys.exit()

input = None
if len(sys.argv) >= 3:
    with open(sys.argv[1]) as f1, open(sys.argv[2]) as f2:
        input = zip([l.strip() for l in f1], [l.strip() for l in f2])
else:
    input = [l.strip().split('\t') for l in sys.stdin]

verbose = '-v' in sys.argv
for i in input:
    if len(i) != 2:
        print >>sys.stderr, i
dists = [edit_distance(s.split(), t.split()) for s, t in input]

if verbose:
    for d in dists:
        print(d)
    print 'Total: ',

print 1.*sum(dists)/len(dists)
