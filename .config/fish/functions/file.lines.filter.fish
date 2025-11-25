# Defined interactively
function file.lines.filter --argument file
    for word in $argv[2..-1]
        if test -n "$word"
            grep -i "$word" "$file"
            grep -iv "$word" "$file" | sponge "$file"
        end
    end
end
