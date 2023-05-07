#!/bin/bash

## you can change path of the output file, ~ is a shortcut to your home directory
#you also can change languages, for maore information type "trans -T" in your terminal

xsel | trans -no-bidi -show-languages no   -show-alternatives no en:ar >~/.scripts/translation.txt &
process_id=$!
wait $process_id

## uncomment your text editor
xed /home/abode/.scripts/translation.txt
# gedit
# kate
# kwrite
