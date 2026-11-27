# Defined interactively
function trash.restore.d.folder --wraps='lb'
    for i in (seq 1 $MERGERFS_DISKS)
        /mnt/d$i/
        mkdir $argv
        lb mv .Trash/1000/files/$argv $argv
    end
end
