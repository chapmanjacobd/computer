# Defined interactively
function filterfile --argument file word
    grep -i "$word" "$file"
    grep -iv "$word" "$file" | sponge "$file"
end
