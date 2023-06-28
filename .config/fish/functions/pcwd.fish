# Defined interactively
function pcwd
    for p in $argv
        readlink -e /proc/$p/cwd
    end
end
