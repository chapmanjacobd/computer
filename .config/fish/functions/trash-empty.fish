# Defined interactively
function trash-empty
    filter_opts $argv

    if test -z "$args"
        echo Error! No mount points passed as args
        return 1
    end

    trash-size
    trash-list >>~/.local/share/trashed.txt

    # for mnt in $argv
    #    for d in $mnt/.Tras*/*/files/
    #        NO_COLOR=1 ncdu "$d"
    #    end
    # end

    if contains -- -f $opts; or gum confirm --default=no 'Empty trash?'
        for mnt in $args
            sudo btrfs subvolume delete --commit-each $mnt/.snapshots/one &
        end

        command trash-empty -f
        wait

        for mnt in $args
            sudo btrfs subvolume snapshot -r $mnt $mnt/.snapshots/one &
        end
        wait
    end

end
