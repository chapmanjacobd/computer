# Defined interactively
function file.lines.dedupe
    cat "$argv" | unique | sponge "$argv"
end
