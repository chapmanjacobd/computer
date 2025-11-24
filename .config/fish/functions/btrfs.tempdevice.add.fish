# Defined via `source`
function btrfs.tempdevice.add --argument-names btrfs_mnt --argument-names new_mnt
    if test (count $argv) -ne 2
        echo "Usage: btrfs.tempdevice.add <btrfs_mountpoint> <new_mountpoint>"
        return 1
    end

    if not test -d "$btrfs_mnt"
        echo "Error: Btrfs mountpoint '$btrfs_mnt' does not exist."
        return 1
    end

    set temp_file (mktemp --tmpdir="$new_mnt")

    echo Using temp file "$temp_file"
    if not truncate -s 20G "$temp_file"
        echo "Error: Failed to create temporary file."
        return 1
    end

    set loop_dev (sudo losetup -f "$temp_file" --show)
    if test $status -ne 0
        echo "Error: Failed to create loopback device."
        return 1
    end
    echo "Loopback device created: $loop_dev"

    if not sudo btrfs device add "$loop_dev" "$btrfs_mnt"
        echo "Error: Failed to add device to Btrfs."
        return 1
    end
end
