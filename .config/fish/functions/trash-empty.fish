# Defined interactively
function trash-empty
    trash-list | tee -a ~/.local/share/trashed.txt
    command trash-empty $argv
    sort --unique --ignore-case ~/.local/share/trashed.txt | sponge ~/.local/share/trashed.txt
    if gum confirm 'Refresh snapshots?'
        for mnt in /mnt/d1 /mnt/d2 /home
            btrfs_check_delete_snapshot $mnt
        end
    end
end
