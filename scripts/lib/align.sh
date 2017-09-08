#!/bin/bash
# this script will estimate and print the alignment of $1  with the large alignment model (fce+nucle+lang8)
# if the model doesn't exist, will create it

if [ $@ -ne 1 ]; then
	echo "./scripts/align.sh corpus/prefix"
fi
corpus="$1"
model=data/alignment/input.err-corr.params

if [[ ! -f "$model" ]]; then
	echo "Training alignment model"
	if [ ! -e data/alignment/input.noblanks ]; then
		echo "User must provide data for training fast align model. we used the train/tune sets from FCE, NUCLE, and LANG8. Each line should have the format ERROR SENTENCE ||| CORRECT SENTENCE"
		exit
	fi
	$FASTALIGN/fast_align -i data/alignment/input.noblanks -s -d -v -o -p $model > $model.out 2> $model.err &
fi

echo "aligning $1..."
mkdir $corpus-align 2>/dev/null
cat $corpus.tok.lc.err $corpus.tok.lc.corr > $corpus-align/corpus.err
cat $corpus.tok.lc.corr $corpus.tok.lc.err > $corpus-align/corpus.corr
paste $corpus-align/corpus.err $corpus-align/corpus.corr | perl -pe 's/\t/ ||| /' > $corpus-align/input

echo "Generating alignment"
$FASTALIGN/fast_align -i $corpus-align.input -f $model | cut -f 7 -d '|' > $corpus.align
echo "alignment saved to $corpus.align"
