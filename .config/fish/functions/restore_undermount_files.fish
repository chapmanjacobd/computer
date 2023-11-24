# Defined interactively
function restore_undermount_files
    sudo mkdir /orig_mnt/
    sudo mount --bind /mnt /orig_mnt/
    /orig_mnt/
    for dir in (fd -td -d1)
        # check if src and dest are the same...
        # may be wise to do manually, if one is wise enough
        NO_COLOR=1 ncdu /orig_mnt/$dir
        if confirm
            rclone move /orig_mnt/$dir /mnt/$dir
        end
    end
end
