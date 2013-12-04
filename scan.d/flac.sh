#!/bin/bash

source $GI2_CONFIGROOT/shared.sh

cd $GI2_TAGROOT

tempfile=`mktemp`

# filter out flac
egrep '.*/music/.*\.flac$' $1 > $tempfile

# iterate over files
while read f
do
	# DO TAGGING CRAP
	
	cleanf=`cleanstring "$f"`
	if [ -r "$cleanf" ]
	then
		# artist
	
#		artist=`eyeD3 "$cleanf" | egrep -o 'artist.*$' | cut -c 13-`
#		cleanartist=`cleanstring "$artist"`
#	
#		if [ ! -z "$cleanartist" ]
#		then
#			filename=`basename "$cleanf"`
#			linkname="$cleanartist""__$filename"
#			targetname=`relpath "$cleanf" artist/`
#			ln -sfv "$targetname" "artist/$linkname"
#		fi
		

		# matching mp3

		mp3name=`echo "$cleanf" | sed 's|/documents/music/|/documents/mp3music/|' | sed 's|.flac|.mp3|'`
		if [ ! -e "$mp3name" ]
		then
			mp3dir=`dirname "$mp3name"`
			mkdir -p "$mp3dir"

			# convert to mp3
			flac2mp3 "$cleanf" "$mp3name"
		fi
	fi
done < $tempfile

rm -f $tempfile

