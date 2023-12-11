#!/usr/bin/env fish

set duplicate $argv[1]
set original $argv[2]

rm "$duplicate"

for n in (seq 1 10)
    set src (echo "$original" | sed "s|/mnt/d/|/mnt/d$n/|")
    if test -e "$src"
        set dest (echo "$duplicate" | sed "s|/mnt/d/|/mnt/d$n/|")
        mkdir (path dirname "$dest")
        cp --reflink=always "$src" "$dest"
    end
end
