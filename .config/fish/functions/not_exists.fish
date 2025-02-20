# Defined interactively
function not_exists
    while read -l path
        if not test -f "$path"
            echo "$path"
        end
    end
end
