# Defined interactively
function popline
    tail -n 1 "$argv"
    sed -i '$ d' "$argv"
end
