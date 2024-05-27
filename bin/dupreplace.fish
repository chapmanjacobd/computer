#!/usr/bin/env fish

# rmlint -c sh:cmd='dupreplace.fish "$1" "$2"'

set duplicate $argv[1]
set original $argv[2]

rm "$duplicate"
lb mergerfs-cp "$original" "$duplicate"
