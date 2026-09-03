# Defined interactively
function rm.secure
    shred -u -z -n 3 $argv

    for target_mount in (df --output=target $argv | tail -n +2 | sort -u)
        sudo fstrim -v "$target_mount"
    end
end
