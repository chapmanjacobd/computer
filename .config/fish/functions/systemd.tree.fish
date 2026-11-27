# Defined via `source`
function systemd.tree --wraps='pstree'
    pstree -a -p (systemctl --user show --value -p MainPID $argv)
end
