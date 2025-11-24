# Defined via `source`
function folder.snapshot.restore
    set snapshot_folder $argv[1]

    if test -d $snapshot_folder
        set folder (path basename (pwd))

        rm -rf ../$folder
        cp --reflink=auto -r $snapshot_folder ../$folder
        # btrfs subvolume snapshot $snapshot_folder ../$folder
    end

    cd ../$folder
end
