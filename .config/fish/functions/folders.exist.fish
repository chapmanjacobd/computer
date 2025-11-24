# Defined via `source`
function folders.exist
    while read -l path
        if test -d "$path"
            echo "$path"
        end
    end
end
