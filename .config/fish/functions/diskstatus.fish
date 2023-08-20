# Defined interactively
function diskstatus
    for mnt in / /mnt/d{1,2,3,4,5,6,7,8,9}
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

    smartls Power_On_Hours Power_Cycle_Count Load_Cycle_Count UDMA_CRC_Error_Count
    smartls Reallocated_Sector_Ct Reallocated_Event_Count Current_Pending_Sector Offline_Uncorrectable

    lb mu /mnt/d{1,2,3,4,5,6,7,8,9}
end
