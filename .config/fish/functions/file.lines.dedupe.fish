# Defined interactively
function file.lines.dedupe --wraps='cat'
    cat "$argv" | unique | sponge "$argv"
end
