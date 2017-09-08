#!/bin/bash
# calls RASP morph generator on $1 and writes to $1.out

if [ $@ -lt 1 ]; then
	echo "call_morphg.sh input1 [input2 ...]"
	exit
fi

if [[ "x$MORPH_HOME" == "x" ]]; then
	echo "set MORPH_HOME to point to your local installation of morpha/morphg"
	exit
fi

mydir=`pwd`
for f in $@; do
	path=`realpath $f`

	cd $MORPH_HOME

	cmd="cat $path | ./morphg > $path.out"
	echo $cmd &>2
	eval $cmd
	cd $mydir
done
