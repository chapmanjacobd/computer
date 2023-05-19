# Defined interactively
function btrfs_nocheck_delete_snapshot --argument mnt
    sudo btrfs subvolume delete --commit-each $mnt/.snapshots/one
    sudo btrfs subvolume snapshot -r $mnt $mnt/.snapshots/one
end
