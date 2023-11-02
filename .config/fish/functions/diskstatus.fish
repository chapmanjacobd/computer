# Defined interactively
function diskstatus
    for mnt in / /mnt/d{1,2,3,4,5,6,7,8,9}
        echo
        echo MOUNTPOINT: $mnt
        echo ---
        sudo btrfs fi usage -T $mnt
        echo
    end

    for mnt in / /mnt/d{1,2,3,4,5,6,7,8,9}
        sudo btrfs device stats $mnt
    end

    sudo smartctl -A /dev/nvme0n1

    smartlba

    smartls Power_On_Hours Power_Cycle_Count Load_Cycle_Count UDMA_CRC_Error_Count
    smartls Reallocated_Sector_Ct Reallocated_Event_Count Current_Pending_Sector Offline_Uncorrectable

    for mnt in / /mnt/d{1,2,3,4,5,6,7,8,9}
        if not sudo btrfs scrub status $mnt | grep -q 'no errors'
            sudo btrfs scrub status $mnt
        end
    end

    lb mu /mnt/d{1,2,3,4,5,6,7,8,9}
end
