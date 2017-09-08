#!/bin/bash

# Evaluates candidates on the JFLEG test set

usage=" ./scripts/eval.sh candidate1 [candidate2]"

if [[ $# -lt 1 || "$1" == "-h" ]]; then
	echo $usage
	exit
fi

if [[ "x$M2HOME" == "x" ]]; then
	echo "Please set M2HOME to point to your installation of the m2scorer"
	exit
fi

home=`dirname $0`
m2ref="$home/data/test/jfleg-test.tok.corr.0-3.m2"
gref="$home/data/test/jfleg-test.tok.corr[0-3]"
src="$home/data/test/jfleg-test.tok.err"

for cand in $@; do
	# calculate how many sentences changed from input
	echo "=======$cand======" >&2
	changed=`paste $cand $src | perl scripts/lib/diff.pl | wc -l`
	echo "$changed changed" >&2
	# edit distance between input and candidate
	ld=`python scripts/lib/levenshtein_distance.py $cand $src`
	echo "LD $ld" >&2
	# M2 score
	m2=`$M2HOME/m2scorer $cand $m2ref | perl -pe 's/\n/ /g' | perl -pe 's/\t:| +:/:/g'`
	echo "M2 $m2" >&2
	# GLEU score
	gleu=`python scripts/lib/calculate_gleu.py -s $src -r $gref -c $cand | perl -pe 's/\n/ /g' | cut -f 2 -d ' '`
	echo "GLEU $gleu" >&2
	echo "$cand\t$changed changed\t$m2\t$gleu\t$ld"
done
