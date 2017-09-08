#!/bin/bash
# does POS tagging and morpha analysis
# assumes that the vocab file is already lowercased and unique
# writes to vocab.morpha

usage="./scripts/generate_morpha_lookup.sh [-d target-dir] file.vocab [file1.vocab ...]"

if [ $# -lt 1 ]; then
	echo "$usage"
	exit
fi

targetdir="store"
thisdir=`pwd`
# read options
while [[ $# -gt 0 ]]; do
	case "$1" in
		-d) targetdir="$2"; shift;;
		-h) echo "$usage"; exit;;
		*) break;;
	esac
	shift
done

targetdir=`realpath $targetdir`

mkdir $targetdir 2> /dev/null

# cat all vocab files and get unique entries
# tag pos
cat $@ | sort | uniq | tee $targetdir/vocab | java -cp $STANFORD_HOME/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model $STANFORD_HOME/models/english-bidirectional-distsim.tagger > $targetdir/vocab.pos
# convert to morpha tags
cat $targetdir/vocab.pos | sh scripts/lib/ptb_to_morph_tags.sh > $targetdir/vocab.pos.morpha-in
# do morph analysis
cd $MORPH_HOME
cat $targetdir/vocab.pos.morpha-in | ./morpha -at > $targetdir/vocab.morpha
cd $thisdir
