# Defined interactively
function pgrep-children
    ps -o etime,%cpu,command ww (children (pgrep $argv))
end
