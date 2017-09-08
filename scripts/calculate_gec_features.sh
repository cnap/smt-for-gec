#!/bin/bash

# Calculate GEC features for grammars passed through the command line

if [ $@ -lt 1 ]; then
	echo "./scripts/calculate_gec_features.sh grammar.gz [grammar1.gz ...]"
	exit
fi

for grammar in $@; do
	newgrammar="${grammar/gz/gec-features.gz}"
	echo "Calculating GEC features for $grammar, saving to $newgrammar..."
	zcat $grammar | python scripts/lib/add_error_features.py | \
		gzip -9 > $newgrammar
	echo "Done"
done
