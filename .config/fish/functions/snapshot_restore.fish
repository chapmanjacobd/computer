# Defined via `source`
function snapshot_restore
    set snapshot_folder $argv[1]

    if test -e $snapshot_folder
        set folder (path basename (pwd))
        trash-put ../$folder
        cp -r $snapshot_folder/ ../$folder/
        # btrfs subvolume snapshot $snapshot_folder $folder
    end
end
