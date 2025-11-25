# Defined interactively
function lines.count
    wc -l $argv | cut -f1 -d' '
end
