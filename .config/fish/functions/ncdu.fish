# Defined interactively
function ncdu
    for s in $argv
        NO_COLOR=1 ncdu $s
    end
end
