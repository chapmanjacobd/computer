# Defined interactively
function pgrep.children
    ps -o pid,etime,%cpu,command ww (ps.children (pgrep $argv))
end
