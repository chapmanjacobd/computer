# Defined interactively
function trash.restore.all
    for n in (seq 1 $MERGERFS_DISKS)
        trash-restore (echo $argv | sed "s|/mnt/d/|/mnt/d$n/|")
    end
end
