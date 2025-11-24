# Defined interactively
function files.exist
    while read -l path
        if test -f "$path"
            echo "$path"
        end
    end
end
