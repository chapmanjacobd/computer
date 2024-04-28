# Defined via `source`
function service-status
    pstree -a -p (systemctl --user show --value -p MainPID $argv)
end
