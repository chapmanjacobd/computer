# Defined interactively
function btrfs.snapshot.delete --argument mnt
    sudo btrfs subvolume delete --commit-each $mnt/.snapshots/one
    sudo btrfs subvolume snapshot -r $mnt $mnt/.snapshots/one
end
