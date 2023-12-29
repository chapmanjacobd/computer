# Defined interactively
function trash-restore-d-folder
    for i in (seq 1 $MERGERFS_DISKS)
        /mnt/d$i/
        trash-restore $argv
    end
end
