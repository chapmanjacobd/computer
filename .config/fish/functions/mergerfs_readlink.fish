# Defined interactively
function mergerfs_readlink
    for n in (seq 1 $MERGERFS_DISKS)
        set f (echo $argv | sed "s|/mnt/d/|/mnt/d$n/|")
        if test -e $f
            echo $f
        end
    end
end
