# Defined interactively
function trash-empty-no-snapshot
    filter_opts $argv

    if test -z "$args"
        set args (trash-list --trash-dirs)
    end

    for mnt in $args
        sudo btrfs subvolume delete --commit-each $mnt/.snapshots/one
    end

    trash-size
    trash-list >>~/.local/share/trashed.txt

    if contains -- -f $opts; or gum confirm --default=no 'Empty trash?'
        command trash-empty -f
    end
end
