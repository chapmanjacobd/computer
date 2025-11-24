# Defined via `source`
function lines.sum
    awk '{s+=$1} END {print s}' "$argv"
end
