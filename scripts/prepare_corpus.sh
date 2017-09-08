#!/bin/bash

# This script will prepare a parallel corpus by tokenizing and generating an alignment.
# Input corpora should be saved in PREFIX.err and PREFIX.corr, one sentence per line.

if [[ $# -ne 2 ]]; then
	echo "./scripts/prepare_corpus.sh PREFIX corpusname [output-dir]
default output-dir is data/"
	exit
fi

if [[ "x$JOSHUA" == "x" ]]; then
	echo "Please set $JOSHUA to point to your installation of Joshua"
	exit
fi

# combine and find changed sentences
orig="$1"
target="data"
if [ $@ -gt 2 ]; then
	$target=$3
fi
corpus="$target/$2"
align="$corpus-alignment"

echo "Preparing corpus from $orig.[err|corr] and saving to $corpus*"

mkdir $target 2> /dev/null

echo "Filtering unchanged sentences"
paste $orig.err $orig.corr | perl scripts/lib/diff.pl > $corpus-parallel.tab

echo "Tokenizing files"
cut -f 1 $corpus-parallel.tab | perl -p -e 's/http:\/\/ ?\S+?/URL/g' | $JOSHUA/scripts/preparation/tokenize.pl > $corpus.tok.err
cut -f 2 $corpus-parallel.tab | perl -p -e 's/http:\/\/ ?\S+?/URL/g' | $JOSHUA/scripts/preparation/tokenize.pl > $corpus.tok.corr

echo "Filtering sentence pairs by length"
python scripts/lib/filter_by_length.py $corpus.tok
mv $corpus.filtered.err $corpus.tok.err
mv $corpus.filtered.corr $corpus.tok.corr

echo "Lowercasing"
cat $corpus.tok.err | perl -ne 'print lc' > $corpus.tok.lc.err
cat $corpus.tok.corr | perl -ne 'print lc' > $corpus.tok.lc.corr

echo "Getting vocabulary"
python scripts/libget_vocab.py $corpus.tok.err $corpus.tok.corr > $corpus.vocab

echo "Tagging POS"
cat $corpus.tok.err | java -cp $STANFORD_HOME/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model $STANFORD_HOME/models/english-bidirectional-distsim.tagger > $corpus.tok.err.pos
cat $corpus.tok.corr | java -cp $STANFORD_HOME/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model $STANFORD_HOME/models/english-bidirectional-distsim.tagger > $corpus.tok.corr.pos

echo "Generating alignment"
sh scripts/lib/align.sh $corpus
