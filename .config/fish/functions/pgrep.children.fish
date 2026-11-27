# Defined interactively
function pgrep.children --wraps='ps'
    ps -o pid,etime,%cpu,command ww (ps.children (pgrep $argv))
end
