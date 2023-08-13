# Defined interactively
function diskstatus
    for mnt in / /mnt/d1 /mnt/d2 /mnt/d3 /mnt/d4 /mnt/d5 /mnt/d6 /mnt/d7
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
        sudo smartctl -A $dev | grep -E 'Reallocated_Sector_Ct|Reallocated_Event_Count|Current_Pending_Sector|Offline_Uncorrectable'
    end
    lb mu /mnt/d{1,2,3,4,5,6,7}
end
