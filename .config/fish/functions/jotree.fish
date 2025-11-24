# Defined via `source`
function jotree
    for pid in (systemctl --user show --value -p MainPID (ls -1 .local/jobs/) | filter-empty-lines | lines.not.0)
        pstree -altp $pid
    end
end
