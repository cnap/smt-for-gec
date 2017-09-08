"""prints unique tokens across all input files"""

import sys
import codecs

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "python scripts/lib/get_vocab.py file1 [file2 ...]"
        sys.exit()

    words = set()
    for f in sys.argv[1:]:
        with codecs.open(f, 'r', 'utf-8') as fin:
            for line in fin:
                for tok in line.strip().split():
                    words.add(tok)
    for w in words:
        print w
