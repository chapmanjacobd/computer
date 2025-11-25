# Defined interactively
function percent.from.float
    awk '{printf "%.2f%%\n", $0 * 100}'
end
