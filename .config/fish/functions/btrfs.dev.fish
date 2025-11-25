# Defined interactively
function btrfs.dev --argument-names btrfs_mount
    sudo btrfs filesystem show --raw "$btrfs_mount" | grep -oP 'path\s+(\S+)' | cut -d' ' -f2
end
