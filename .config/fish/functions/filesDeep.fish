# Defined in - @ line 2
function filesDeep --argument location reverse
    set loc (default $location .)
    find $loc -not -type d -exec du -h {} + | sort -h $reverse | cut -f2
end
