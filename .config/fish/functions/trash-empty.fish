# Defined interactively
function trash-empty
    if test -z "$argv"
        echo Error! No mount points passed as args
        return 1
    end

    trash-size
    trash-list >> ~/.local/share/trashed.txt

    # for mnt in $argv
    #    for d in $mnt/.Tras*/*/files/
    #        NO_COLOR=1 ncdu "$d"
    #    end
    # end

    if gum confirm --default=no 'Empty trash?'
        command trash-empty -f

    # if gum confirm --default=no 'Refresh snapshots?'
        for mnt in $argv
            btrfs_nocheck_delete_snapshot $mnt
            #kitty fish -c "sleep (random_thousanths 0 5000); btrfs_check_delete_snapshot $mnt" &
        end
        wait
    # end
    end

end
