# Defined interactively
function filter-deleted
    while read -l line
        if test -e $line
            echo $line
        end
    end
end
