# Defined interactively
function file.line.pop --wraps='tail'
    tail -n 1 "$argv"
    sed -i '$ d' "$argv"
end
