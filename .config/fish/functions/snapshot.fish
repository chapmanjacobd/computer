# Defined via `source`
function snapshot
    set folder (path basename (pwd))
    set snapshot_folder $folder-(date +"%Y%m%d-%H%M%S")-snapshot

    echo folder.snapshot.restore ../$snapshot_folder
    cp --reflink=auto -r ../$folder ../$snapshot_folder
    # btrfs subvolume snapshot -r ../$folder ../$snapshot_folder
end
