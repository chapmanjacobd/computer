#!/bin/bash
set -e

# spekk - audio spectrogram creator
# ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin
#
# example usage:
# find -mindepth 1 -maxdepth 1 -name \*.mp3 -exec spekk '{}' \;

td=$(mktemp -d)
trap "trap - EXIT; rm -rf $td; exit" EXIT

ffmpeg -i "$1" $td/spectrogram.wav < /dev/null

sox $td/spectrogram.wav -c 1 -t sox - gain -n -B |
sox -V -t sox - -n spectrogram -x 1820 -y 1025

mv spectrogram.png "$1.png"
