# Defined interactively
function diskstatus
    for mnt in / (mergerfs.disk.mounts)
        sudo btrfs device stats $mnt
    end

    sudo smartctl -A /dev/nvme0n1

    smartctl.lbas

    smartctl.ls Power_On_Hours Power_Cycle_Count Load_Cycle_Count UDMA_CRC_Error_Count
    smartctl.ls Reallocated_Sector_Ct Reallocated_Event_Count Current_Pending_Sector Offline_Uncorrectable

    for mnt in / (mergerfs.disk.mounts)
        if not sudo btrfs scrub status $mnt | grep -q 'no errors'
            echo $mnt
            sudo btrfs scrub status $mnt
        end
    end

    mount.ro

    lb mu (mergerfs.disk.mounts)
end
