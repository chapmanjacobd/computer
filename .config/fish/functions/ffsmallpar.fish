# Defined interactively
function ffsmallpar
    set tmpfile (mktemp)
    fd -S+200MB | grep -v .small. >$tmpfile
    cat $tmpfile | parallel --dry-run
end
