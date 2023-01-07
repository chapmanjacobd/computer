# Defined via `source`
function gitls
    for f in *
        git log -1 --date=iso-strict-local --format="%ad %>(12) %cr %<(10) %an %x09 %h  $f" -- "$f"
    end | sort --general-numeric-sort

end
