#!/bin/fish
for f in $argv
    printf "# file: %s\n\n" $f
    cat $f
    echo
end
