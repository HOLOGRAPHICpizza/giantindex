#!/bin/bash

source $GI2_CONFIGROOT/shared.sh

cd $GI2_TAGROOT

tempfile=`mktemp`

# filter out mp3
egrep '.*\.mp3$' $1 > $tempfile

# iterate over files
while read f
do
	# DO TAGGING CRAP
	
	cleanf=`cleanstring "$f"`
	if [ -r "$cleanf" ]
	then
		artist=`eyeD3 "$cleanf" | egrep -o 'artist.*$' | cut -c 13-`
		cleanartist=`cleanstring "$artist"`
	
		if [ ! -z "$cleanartist" ]
		then
			filename=`basename "$cleanf"`
			linkname="$cleanartist""__$filename"
			targetname=`relpath "$cleanf" artist/`
			ln -sfv "$targetname" "artist/$linkname"
		fi
	fi
done < $tempfile

rm -f $tempfile

