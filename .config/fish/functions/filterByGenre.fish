# Defined in - @ line 1
function filterByGenre
    while read file
        if ffprobe "$file" 2>&1 | sed -E -n 's/^ *GENRE *: (.*)/\1/p' | grep -q "$argv"
            echo "$file"
        end
    end
end
