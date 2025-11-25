# Defined via `source`
function jo.tree
    for pid in (systemctl --user show --value -p MainPID (ls -1 .local/jobs/) | lines.not.empty | lines.not.0)
        pstree -altp $pid
    end
end
