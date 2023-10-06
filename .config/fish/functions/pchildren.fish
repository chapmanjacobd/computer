# Defined interactively
function pchildren
    pstree -lap (pgrep -n $argv)
end
