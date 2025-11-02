# Defined interactively
function unparallel
    ps -o etime,state,%mem,%cpu -p (pgrep $argv)
    presume-all
    ppause (pgrep $argv | offset 3)

    while sleep 5m
        ps -o etime,state,%mem,%cpu -p (pgrep $argv)
        presume-all
        ppause (pgrep $argv | offset 5)
    end
end
