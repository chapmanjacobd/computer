# Defined interactively
function btrfs.snapshot.delete.check -a mnt
    if not string length --quiet $mnt
        echo Please specify mount point as first arg
        return 1
    end

    sudo btrfs subvolume snapshot -r $mnt $mnt/.snapshots/two

    set tmp_diff (mktemp /tmp/btrfs_diffXXXXX)
    sudo btrfs send --no-data -p $mnt/.snapshots/one $mnt/.snapshots/two >$tmp_diff

    #~/bin/btrfs-snapshots-diff-summary.py --by_path -t -f $tmp_diff
    ~/bin/btrfs-snapshots-diff-summary.py -f $tmp_diff --stats
    echo sudo ~/.cargo/bin/btsdu -p $mnt/.snapshots/two $mnt/.snapshots/one

    if gum confirm --default=no 'Swap snapshots?'
        sudo btrfs subvolume delete --commit-each $mnt/.snapshots/one
        command mv $mnt/.snapshots/two $mnt/.snapshots/one
    else
        sudo btrfs subvolume delete --commit-each $mnt/.snapshots/two
    end

    rm $tmp_diff
end
