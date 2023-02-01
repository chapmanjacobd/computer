# Defined interactively
function trash-empty
    if gum confirm --default=no 'Refresh snapshots?'
        for mnt in $D_DISKS /home
            btrfs_check_delete_snapshot $mnt
        end
    end

    trash-list | tee -a ~/.local/share/trashed.txt
    command trash-empty -f $argv
end
