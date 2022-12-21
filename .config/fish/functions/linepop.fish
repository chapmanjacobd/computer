# Defined interactively
function linepop
    tail -n 1 "$argv"
    sed -i '$ d' "$argv"
end
