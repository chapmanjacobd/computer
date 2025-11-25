# Defined interactively
function paths.exists.no
    while read -l path
        if not test -f "$path"
            echo "$path"
        end
    end
end
