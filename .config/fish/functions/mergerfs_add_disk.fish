# Defined interactively
function mergerfs_add_disk --argument dev label
    sudo mkfs.btrfs -R free-space-tree -m dup -d single $dev -L $label # ie. d1
    sudo btrfs inspect-internal dump-super -f $dev | sudo tee /mnt/superblocks/$label
    kitty fish -c fstab

    sudo mkdir /mnt/$label
    sudo chown xk:xk /mnt/$label
    sudo systemctl daemon-reload
    mount /mnt/$label
    sudo chown xk:xk /mnt/$label
    sudo mergerfs.ctl -m /mnt/d add path /mnt/$label
    sudo mergerfs.ctl -m /mnt/d info
    sudo mergerfs.mktrash /mnt/d
    df -h
end
