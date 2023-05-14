# Defined interactively
function trash-empty
    trash-size
    trash-list | tee -a ~/.local/share/trashed.txt

    for mnt in $argv
        for d in $mnt/.Tras*/*/files/
            NO_COLOR=1 ncdu "$d"
        end
    end

    if gum confirm --default=no 'Empty trash?'
        command trash-empty -f
    end

    if gum confirm --default=no 'Refresh snapshots?'
        for mnt in $argv
            kitty fish -c "sleep (random_thousanths 0 5000); btrfs_check_delete_snapshot $mnt" &
        end
        wait
    end


end
