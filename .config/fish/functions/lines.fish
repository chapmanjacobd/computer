# Defined interactively
function lines
    wc -l $argv | cut -f1 -d' '
end
