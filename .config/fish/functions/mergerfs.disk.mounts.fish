# Defined interactively
function mergerfs.disk.mounts
    for n in (seq 1 $MERGERFS_DISKS)
        echo /mnt/d$n
    end
end
