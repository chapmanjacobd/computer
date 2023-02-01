# Defined interactively
function diskstatus
    for mnt in / $D_DISKS
        echo
        echo MOUNTPOINT: $mnt
        echo ---
        sudo btrfs fi usage -T $mnt
        echo
        sudo btrfs device stats -T $mnt
        echo
        sudo btrfs scrub status $mnt
        echo ---
        echo
    end
    for dev in /dev/sd*
        echo $dev
        sudo smartctl -A $dev | grep -E 'Reallocated_Sector_Ct|Current_Pending_Sector|Offline_Uncorrectable'
    end
end
