# Defined via `source`
function jotree
    for pid in (systemctl --user show --value -p MainPID (ls -1 .local/jobs/) | filter-empty-lines)
        pstree -altp $pid
    end
end
