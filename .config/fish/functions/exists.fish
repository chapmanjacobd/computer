# Defined interactively
function exists
    while read -l path
        if test -f "$path"
            echo "$path"
        end
    end
end
