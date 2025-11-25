# Defined interactively
function file.line.pop
    tail -n 1 "$argv"
    sed -i '$ d' "$argv"
end
