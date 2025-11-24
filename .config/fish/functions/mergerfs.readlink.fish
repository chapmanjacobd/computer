# Defined interactively
function mergerfs.readlink
    for n in (seq 1 $MERGERFS_DISKS)
        set f (path resolve $argv | sed "s|/mnt/d/|/mnt/d$n/|")
        if test -e $f
            echo $f
        end
    end
end
