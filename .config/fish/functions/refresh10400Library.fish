# Defined interactively
function refreshpakonLibrary
    for db in audio video tax
        rsync -auh --info=progress2 --no-inc-recursive xk@pakon:/home/xk/lb/$db.db sshfs_$db.db
    end
end
