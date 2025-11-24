# Defined interactively
function paths.exist
    while read -l line
        if test -e $line
            echo $line
        end
    end
end
