# Defined via `source`
function service-status
    pstree -a -p (pgrep -f $argv)
end
