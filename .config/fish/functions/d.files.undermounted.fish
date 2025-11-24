# Defined via `source`
function d.files.undermounted
    sudo mkdir /orig_mnt/
    sudo mount --bind /mnt /orig_mnt/
    /orig_mnt/
    for dir in (fd -td -d1)
        # check if src and dest are the same...
        # may be wise to do manually, if one is wise enough--or prevent this to begin with via conventional mountpoint dir permissions
        NO_COLOR=1 ncdu /orig_mnt/$dir
        if confirm
            lb mv /orig_mnt/$dir /mnt/$dir
        end
    end
end
