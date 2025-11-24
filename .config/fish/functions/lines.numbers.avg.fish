# Defined interactively
function lines.numbers.avg
    awk '{s+=$1}END{print s/NR}' "$argv"
end
