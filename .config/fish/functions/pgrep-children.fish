# Defined interactively
function pgrep-children
    ps -o pid,etime,%cpu,command ww (proc.children (pgrep $argv))
end
