# Defined interactively
function delete_duplicate_lines
    cat "$argv" | unique | sponge "$argv"
end
