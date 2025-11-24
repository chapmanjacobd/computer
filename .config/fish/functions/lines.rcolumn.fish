# Defined interactively
function lines.rcolumn
    awk '{print $(NF-'(coalesce $argv 0)')}'
end
