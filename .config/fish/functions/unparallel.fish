# Defined interactively
function unparallel
    presume-all
    ppause (pgrep $argv | offset 4)
    ps -o etime,state,%mem,%cpu -p (pgrep $argv)

    while sleep 30s
        presume-all
        ppause (pgrep $argv | offset 6)
        ps -o etime,state,%mem,%cpu -p (pgrep $argv)
    end
end
