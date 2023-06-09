# Defined interactively
function linetail
    awk '{print $(NF-'(coalesce $argv 0)')}'
end
