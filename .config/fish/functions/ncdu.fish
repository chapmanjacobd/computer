# Defined interactively
function ncdu -w ncdu
    for s in $argv
        NO_COLOR=1 command ncdu $s
    end
end
