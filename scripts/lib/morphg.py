#!/usr/bin/env python3
"""
Wrapper around morphg from
http://www.informatics.sussex.ac.uk/research/groups/nlp/carroll/morph.html

Vaguely follows edu.stanford.nlp.Morphology except we implement with a pipe.
hacky.  Would be nice to use cython/swig/ctypes to directly embed morphg.yy.c
as a python extension.

TODO compare linguistic quality to lemmatizer in python's "pattern" package

By Brendan O'Connor (http://brenocon.com), at https://gist.github.com/brendano/6008945
"""
import sys
import os,subprocess

MorphgDir = os.environ('MORPH_HOME')
MorphgCmd = os.path.join(MorphgDir, 'morphg.pipe')
MorphgArgs= ['-f', os.path.join(MorphgDir, 'verbstem.list')]

_pipe = None

def get_pipe():
    global _pipe
    if _pipe is None:
        open_pipe()
    elif _pipe.returncode is not None:
        sys.stderr.write("Pipe seems to have died, restarting\n")
        open_pipe()
    return _pipe

def open_pipe():
    global _pipe
    sys.stderr.write("Opening morphg pipe\n")
    _pipe = subprocess.Popen([MorphgCmd] + MorphgArgs, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def process(input):
    input = input.strip()
    output = None
    for retry in range(3):
        try:
            pipe = get_pipe()
            pipe.stdin.write((input + '\n').encode('utf-8'))
            pipe.stdin.flush()
            output = pipe.stdout.readline().decode('utf-8')
        except IOError:
            if retry==2: raise
            sys.stderr.write("Retry on pipe breakage\n")
            open_pipe()
    return output.rstrip('\n')


## From morph/doc.txt....

#Where the -u option is not used, each input token is expected to be of
#the form <word>_<tag>. For example:
#
#   A_AT1 move_NN1 to_TO stop_VV0 Mr._NNS Gaitskell_NP1 from_II nominating_VVG
#
#Contractions and punctuation must have been separated out into separate
#tokens. The tagset is assumed to resemble CLAWS-2, in the following
#respects:
#
#   V...      all verbs
#   NP...     all proper names
#   N[^P]...  all common nouns
#
#and for specific cases of ambiguous lexical items:
#
#   'd_VH...  root is 'have'
#   'd_VM...  root is 'would'
#   's_VBZ... root is 'be'
#   's_VHZ... root is 'have'
#   's_$...   possessive morpheme (also _POS for CLAWS-5)
#   ai_VB...  root is 'be'
#   ai_VH...  root is 'have'
#   ca_VM...  root is 'can'
#   sha_VM... root is 'shall'
#   wo_VM...  root is 'will'
#   n't_XX... root is 'not'

def ptb_is_proper(ptb):
    return ptb in ('NP','NNP','NNPS')

def ptb2morphtag(ptb):
    ptb = ptb.upper()
    if ptb.startswith('V'):
        return 'V'
    if ptb_is_proper(ptb):
        return 'NP'
    if ptb.startswith('N'):
        return 'N'
    if ptb == 'MD':
        return 'V'   # um is this right?  it looks like it can take incomplete versions...
    if ptb == 'POS':
        return '$'
    return ''
