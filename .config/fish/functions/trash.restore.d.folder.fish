# Defined interactively
function trash.restore.d.folder
    for i in (seq 1 $MERGERFS_DISKS)
        /mnt/d$i/
        mkdir $argv
        lb merge-folder .Trash/1000/files/$argv $argv
    end
end
