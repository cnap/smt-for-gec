#!/bin/bash
## compares parallel English text and quantifies types of changes made

usage="./scripts/compare_edits.sh -i system_input -c system_output [-d]
    -d indicates that the intermediate files should be regenerated"
clean="n"
mydir=`pwd`

while [[ $# -gt 0 ]]; do
	case "$1" in
		-o) output="$2"; shift;;
		-c) input="$2"; shift;;
		-d) clean="y";;
		*) echo "$usage"; exit;;
	esac
	shift
done

if [[ "$clean" == "y" ]]; then
   rm $input.pos
   rm $output.pos
   rm $input.morph
   rm $output.morph
fi

# 1. get alignment

prefix="$output-source.parallel"

echo "aligning sentenes"
paste $input $output | perl -pe 's/\t/ ||| /' > $prefix
if [[ ! -f "$prefix.align" ]]; then
	sh scripts/lib/align.sh $prefix
fi

# 2. get POS tags and morph analysis
echo "performing morphological analysis"
for f in $input $output; do
	if [[ ! -f "$f.pos" ]]; then
		cat $f | java -cp $STANFORD_HOME/stanford-postagger.jar \
					  edu.stanford.nlp.tagger.maxent.MaxentTagger \
					  -model $STANFORD_HOME/models/english-bidirectional-distsim.tagger \
					  -sentenceDelimiter "\\n" > $f.pos
	fi
	if [[ ! -f "$f.morph" ]]; then
		path=`realpath $f`
		cd $MORPH_HOME
		cat $path.pos | ./morpha -at > $path.morph
		cd $mydir
	fi
done

# 3. analyze output
echo "performing analysis"
paste $input.morph $output.morph $prefix.align $input $output | perl -pe 's/\t/ ||| /g' | tee $prefix.full | \
	python scripts/lib/analyze_parallel_sents.py > $prefix.analysis
echo "Done. Analysis saved to $prefix.analysis"
