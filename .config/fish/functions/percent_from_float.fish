# Defined interactively
function percent_from_float
    awk '{printf "%.2f%%\n", $0 * 100}'
end
