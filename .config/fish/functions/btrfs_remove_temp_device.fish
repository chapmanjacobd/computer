# Defined via `source`
function btrfs_remove_temp_device --argument-names btrfs_mount
    if test (count $argv) -ne 1
        echo "Usage: btrfs_remove_temp_device <btrfs_mountpoint>"
        return 1
    end

    if not test -d "$btrfs_mount"
        echo "Error: Btrfs mountpoint '$btrfs_mount' does not exist."
        return 1
    end

    for dev_lo in (sudo btrfs filesystem show --raw "$btrfs_mount" | grep -oP 'path\s+(\S+)' | cut -d' ' -f2)
        if contains -- "$dev_lo" (losetup -O NAME --noheadings)
            while not sudo btrfs device remove --enqueue "$dev_lo" "$btrfs_mount"
                sleep 10
            end

            set -l back_files (losetup "$dev_lo" -O BACK-FILE --noheadings)
            losetup --detach "$dev_lo"
            and rm $back_files
        end
    end
end
