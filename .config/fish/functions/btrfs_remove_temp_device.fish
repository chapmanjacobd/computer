# Defined interactively
function btrfs_remove_temp_device --argument-names btrfs_mount

    for s in (sudo btrfs filesystem show --raw "$btrfs_mount" | grep -oP 'path\s+(\S+)' | cut -d' ' -f2)

        if contains -- "$s" (losetup -O NAME --noheadings)
            while not sudo btrfs device remove --enqueue "$s" "$btrfs_mount"
                sleep 10
            end

            set -l back_files (losetup "$s" -O BACK-FILE --noheadings)
            losetup --detach "$s"
            rm $back_files
        end
    end
end
