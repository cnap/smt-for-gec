#!/bin/bash
# generates artificial spelling and morphplogical rules
# must have already called generate_morpha_lookup.sh

if [ $@ -ne 2 ]; then
	echo "./scripts/create_artificial_rules.sh data/corpus/prefix path/to/lm"
	exit
fi

corpus="$1"
lmpath="$2"

echo "Generating spelling rules..."
python scripts/lib/add_sp_rules.py --prefix $corpus --lm $lmpath | gzip > $corpus/spelling-rules.gz
echo "done"

echo "Generating morphological rules..."
python scripts/lib/generate_morph_rules.py store/vocab | gzip > $corpus/morph-rules.gz
echo "done"
