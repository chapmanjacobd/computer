# Defined via `source`
function pchildren --wraps=pgrep
    pstree -lap (pgrep -n $argv)
end
