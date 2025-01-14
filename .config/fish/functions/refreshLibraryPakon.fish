# Defined interactively
function refreshLibraryPakon
    for db in audio video tax
        rsync -auh --info=progress2 --no-inc-recursive xk@pakon:/home/xk/lb/fs/$db.db sshfs_$db.db
    end
end
