# Defined via `source`
function sum_awk
    awk '{s+=$1} END {print s}' "$argv"
end
