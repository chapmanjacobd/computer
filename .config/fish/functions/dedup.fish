# Defined interactively
function dedup
    awk '!seen[$0]++'
end
