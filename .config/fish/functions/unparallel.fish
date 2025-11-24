# Defined interactively
function unparallel
    ps.resume-all
    ps.pause (pgrep $argv | offset 4)
    ps -o etime,state,%mem,%cpu -p (pgrep $argv)

    while sleep 30s
        ps.resume-all
        ps.pause (pgrep $argv | offset 6)
        ps -o etime,state,%mem,%cpu -p (pgrep $argv)
    end
end
