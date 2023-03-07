# Defined in - @ line 2
function files --argument location reverse
    set loc (default $location .)
    find $loc -maxdepth 1 -not -type d -exec du -h {} + | sort -h $reverse | cut -f2
end
