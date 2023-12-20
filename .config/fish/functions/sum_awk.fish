# Defined interactively
function sum_awk
    awk '{s+=$1} END {print s}'
end
