#!/usr/bin/env bash

# G I A N T I N D E X 2
# v1.0

if [ -z $1 ]
then
	echo "USAGE: scan.sh config/file/path"
	exit 1
fi

source $1
cd $GI2_CONFIGROOT
source shared.sh

scandir () {
	# find all files modified since last scan
	
	lastscan="$1/.GI2_lastscan"
	scanlist="$1/.GI2_scanlist"
	scratch=`mktemp`
	
	if [ ! -e $lastscan ]
	then
		# create file dated for FOREVER AGO
		touch -t 9001010101 $lastscan
	fi
	
	find $1 -newer $lastscan > $scanlist
	
	# filter out excluded files
	while read e
	do
		cp $scanlist $scratch
		grep -v $e $scratch > $scanlist
	done < exclude.txt
	rm -f $scratch
	
	# run all scan scripts in parallel
	for SCRIPT in ./scan.d/*
	do
		if [ -f $SCRIPT -a -x $SCRIPT ]
		then
			echo "$SCRIPT $scanlist" >> $scratch
		fi
	done
	cat $scratch | parallel
	
#	touch $lastscan
	rm -f $scratch
}

# scan each included directory
while read i
do
	scandir $i
done < include.txt

