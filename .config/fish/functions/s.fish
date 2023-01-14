# Defined interactively
function s --argument fn file
    cat "$file" | $fn | sponge "$file"
end
