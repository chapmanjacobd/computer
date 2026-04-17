# Defined interactively
function lines.count
    for s in $argv
        wc -l "$s" | cut -f1 -d' '
    end
end
