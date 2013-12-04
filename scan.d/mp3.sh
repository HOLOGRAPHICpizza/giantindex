#!/bin/bash

source $GI2_CONFIGROOT/shared.sh

cd $GI2_TAGROOT

tempfile=`mktemp`

# filter out mp3
egrep '.*/music/.*\.mp3$' $1 > $tempfile

# iterate over files
while read f
do
	# DO TAGGING CRAP
	
	cleanf=`cleanstring "$f"`
	if [ -r "$cleanf" ]
	then
		# artist
	
		artist=`eyeD3 "$cleanf" | egrep -o 'artist.*$' | cut -c 13-`
		cleanartist=`cleanstring "$artist"`
	
		if [ ! -z "$cleanartist" ]
		then
			filename=`basename "$cleanf"`
			linkname="$cleanartist""__$filename"
			targetname=`relpath "$cleanf" artist/`
			ln -sfv "$targetname" "artist/$linkname"
		fi
		

		# matching mp3

		mp3name=`echo "$cleanf" | sed 's|/documents/music/|/documents/mp3music/|'`
		if [ ! -e "$mp3name" ]
		then
			# link to the mp3
			mp3dir=`dirname "$mp3name"`
			targetname=`relpath "$cleanf" "$mp3dir"`
			mkdir -p "$mp3dir"
			ln -s "$targetname" "$mp3name"
		fi
	fi
done < $tempfile

rm -f $tempfile

