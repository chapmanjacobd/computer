# Defined interactively
function unparallel
    ps -o etime,state,%mem,%cpu -p (pgrep $argv)
    presume-all
    ppause (pgrep $argv | tail -n12)

    while sleep 5m
        ps -o etime,state,%mem,%cpu -p (pgrep $argv)
        presume-all
        ppause (pgrep $argv | tail -n10)
    end
end
