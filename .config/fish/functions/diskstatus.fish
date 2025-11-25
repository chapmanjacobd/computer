# Defined interactively
function diskstatus
    for mnt in / (mergerfs_disk_mounts)
        sudo btrfs device stats $mnt
    end

    sudo smartctl -A /dev/nvme0n1

    smartlba

    smartls Power_On_Hours Power_Cycle_Count Load_Cycle_Count UDMA_CRC_Error_Count
    smartls Reallocated_Sector_Ct Reallocated_Event_Count Current_Pending_Sector Offline_Uncorrectable

    for mnt in / (mergerfs_disk_mounts)
        if not sudo btrfs scrub status $mnt | grep -q 'no errors'
            echo $mnt
            sudo btrfs scrub status $mnt
        end
    end

    mount.ro

    lb mu (mergerfs_disk_mounts)
end
