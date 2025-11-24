# Defined interactively
function trash.restore.here
    for n in (seq 1 $MERGERFS_DISKS)
        set f /mnt/d$n/.Trash/1000/files/(path basename $argv)
        if test -e $f
            mv $f .
        end
    end
end
