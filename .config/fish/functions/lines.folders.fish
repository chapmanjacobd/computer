# Defined interactively
function lines.folders
    while read -l line
        if string length -q $line; and test -d "$line"
            echo "$line"
        end
    end
end
