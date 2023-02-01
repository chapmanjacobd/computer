# Defined interactively
function mergerfs_add_disk --argument part label
    sudo mkfs.btrfs -R free-space-tree -m dup -d single $part -L $label # ie. d1
    kitty fish -c fstab
    sudo btrfs inspect-internal dump-super -f $part | sudo tee /mnt/superblocks/$label

    sudo mkdir /mnt/$label
    sudo chown xk:xk /mnt/$label
    sudo systemctl daemon-reload
    mount /mnt/$label
    sudo chown xk:xk /mnt/$label
    sudo mergerfs.ctl -m /mnt/d add path /mnt/$label
    sudo mergerfs.ctl -m /mnt/d info
    sudo mergerfs.mktrash /mnt/d
    mkdir /mnt/$label/.snapshots
    set --universal --append D_DISKS /mnt/$label
    btrfs_check_delete_snapshot /mnt/$label
    df -h
end
