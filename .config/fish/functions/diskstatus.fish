# Defined interactively
function diskstatus
    for mnt in / /mnt/d1 /mnt/d2 /mnt/d3 /mnt/d4
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
    for dev in /dev/sd* /dev/nvme0n1
        echo $dev
        sudo smartctl -A $dev | grep -E 'Reallocated_Sector_Ct|Current_Pending_Sector|Offline_Uncorrectable'
    end
end
