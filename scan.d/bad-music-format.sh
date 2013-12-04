#!/bin/bash

source $GI2_CONFIGROOT/shared.sh

cd $GI2_TAGROOT

tempfile=`mktemp`
temp2=`mktemp`

# only music
egrep '.*/music/.*' "$1" > $tempfile
cp "$tempfile" "$temp2"

# remove flac
egrep -v '.*\.flac$' "$temp2" > $tempfile
cp "$tempfile" "$temp2"

# remove mp3
egrep -v '.*\.mp3$' "$temp2" > $tempfile
cp "$tempfile" "$temp2"

# remove jpg
egrep -v '.*\.jpg$' "$temp2" > $tempfile
cp "$tempfile" "$temp2"

# remove m3u
egrep -v '.*\.m3u$' "$temp2" > $tempfile
cp "$tempfile" "$temp2"

# remove cue
egrep -v '.*\.cue$' "$temp2" > $tempfile
cp "$tempfile" "$temp2"

# remove png
egrep -v '.*\.png$' "$temp2" > $tempfile

rm -f $temp2

# iterate over files
while read f
do
	cleanf=`cleanstring "$f"`
	cleanftrim=`echo "$cleanf" | cut -c 31-`
	if [ -r "$cleanf" ]
	then
		if [ ! -d "$cleanf" ]
		then
			#TODO: rename jpeg and uppercase extensions
			echo "$cleanftrim"
		fi
	else
		echo "WARNING: $cleanftrim UNREADABLE OR MALFORMED"
	fi
done < $tempfile

rm -f $tempfile
rm -f $temp2

