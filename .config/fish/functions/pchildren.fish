# Defined interactively
function pchildren
    pstree -la (pgrep -n $argv)
end
