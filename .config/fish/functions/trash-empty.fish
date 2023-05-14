# Defined interactively
function trash-empty
    trash-size
    trash-list | tee -a ~/.local/share/trashed.txt

    if test (hostname) = pakon
        for d in /mnt/d{1,2,3,4,5,6,7}/.Tras*/*/files/
            NO_COLOR=1 ncdu $d
        end

        if gum confirm --default=no 'Empty trash?'
            command trash-empty -f $argv
        end

        if gum confirm --default=no 'Refresh snapshots?'
            for mnt in /mnt/d1 /mnt/d2 /mnt/d3 /mnt/d4 /mnt/d5 /mnt/d6 /mnt/d7 /home
                kitty fish -c "btrfs_check_delete_snapshot $mnt" &
            end
            wait
        end

    else
        if gum confirm --default=no 'Empty trash?'
            command trash-empty -f $argv
        end
    end

end
