# Defined via `source`
function systemd.tree
    pstree -a -p (systemctl --user show --value -p MainPID $argv)
end
