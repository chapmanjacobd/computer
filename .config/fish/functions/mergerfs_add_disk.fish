# Defined interactively
function mergerfs_add_disk --argument dev label
    sudo mkfs.btrfs -R free-space-tree -m dup -d single $dev -L $label # ie. d1
    echo run fstab to add the disk. copy the UUID from above
    kitty fish -c fstab
    sudo btrfs inspect-internal dump-super -f $dev | sudo tee /mnt/superblocks/$label

    sudo mkdir /mnt/$label
    sudo chown xk:xk /mnt/$label
    mount /mnt/$label
    sudo mergerfs.ctl -m /mnt/d add path /mnt/$label
    sudo mergerfs.ctl -m /mnt/d info
    df -h
end
