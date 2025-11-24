# Defined interactively
function ps.cwd
    for p in $argv
        readlink -e /proc/$p/cwd
    end
end
