# Defined interactively
function avg
    awk '{s+=$1}END{print s/NR}' "$argv"
end
