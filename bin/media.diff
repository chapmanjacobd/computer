#!/bin/bash
set -e

# mcmp - verify that the decoded contents in multimedia files are equal
# ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin
#
# compare the audio/video frames in two multimedia files after decoding,
# for example an mkv file and an mp4 file

diff \
  <(ffmpeg -hide_banner -nostdin -nostats -y -i "$1" -map 0 -c copy -f framemd5 - 2>&1) \
  <(ffmpeg -hide_banner -nostdin -nostats -y -i "$2" -map 0 -c copy -f framemd5 - 2>&1)
