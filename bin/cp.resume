#!/bin/bash
set -e

# cpr - resume copying a file or blockdevice to a file
# ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin

[ -z "$2" ] && {
	echo "need arg 1: input file"
	echo "need arg 2: output file"
	exit 1
}

ifn="$1"
ofn="$2"
bs=8192

srcvol="$(
	df -h "$1" |
	awk 'NR==2 {print $1}'
)"
[[ $srcvol == /dev/sr* ]] &&
	bs=$(
		isoinfo -d -i /dev/sr0 |
		awk '/^Logical block size/ {print $NF}')

isz=$(stat -c%s -- "$ifn")
osz=$(stat -c%s -- "$ofn")

seek=$((osz/bs))
trunc=$((seek*bs))

printf '\n\033[36minput dev\033[0m   %s\n\033[36minput path\033[0m  %s\n\033[36moutput path\033[0m %s\n\033[36minput size\033[0m  %s\n\033[36moutput size\033[0m %s\n\033[36mbuffer size\033[0m %s\n\033[36mfile offset\033[0m %s\n' \
  "$srcvol" "$ifn" "$ofn" "$isz" "$osz" "$bs" "$seek"

[ $isz -ge $osz ] && {
	echo
	echo "input size greater or equal to output size!"
	echo "nothing to do, exiting"
	exit 0
}

[ $osz -eq $trunc ] || {
	echo
	echo "will truncate output by $((osz-trunc)) bytes ($trunc) before start,"
	echo "press ENTER to accept"
	read -r
	truncate -s $trunc "$ofn"
}

echo now copying...

pv="$(which pv 2>/dev/null)" || pv=cat

dd if="$ifn" bs=$bs skip=$seek conv=sync,noerror | $pv >> "$ofn"

touch -r "$ifn" -- "$ofn"
