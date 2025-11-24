# Defined interactively
function mergerfs.add.disk --argument part label
    sudo mkfs.btrfs -m dup -d single $part -L $label # ie. d1
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
    sudo btrfs subvolume snapshot -r /mnt/$label /mnt/$label/.snapshots/one
    df -h
end
