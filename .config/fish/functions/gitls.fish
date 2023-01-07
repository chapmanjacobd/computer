# Defined via `source`
function gitls
    set -l files
    for f in $argv
        set -a files $f/*
    end
    if not string length --quiet $files
        set files *
    end

    for f in $files
        git log -1 --date=iso-strict-local --format="%ad %>(12) %cr %<(10) %an %x09 %h  $f" -- "$f"
    end | sort --general-numeric-sort
end
