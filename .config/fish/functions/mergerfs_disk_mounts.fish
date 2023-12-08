# Defined interactively
function mergerfs_disk_mounts
    for n in (seq 1 $MERGERFS_DISKS)
        echo /mnt/d$n
    end
end
