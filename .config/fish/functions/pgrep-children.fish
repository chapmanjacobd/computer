# Defined interactively
function pgrep-children
    ps -o pid,etime,%cpu,command ww (children (pgrep $argv))
end
