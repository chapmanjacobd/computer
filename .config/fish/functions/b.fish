# Defined interactively
function b
    maxmem10 fish -c (string join -- ' ' (string escape -- $argv)) &
end
