# Defined via `source`
function sum
    awk '{s+=$1} END {print s}' "$argv"
end
