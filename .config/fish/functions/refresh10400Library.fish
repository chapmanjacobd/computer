# Defined interactively
function refresh10400Library
    for db in audio video tax
        rsync -auh --info=progress2 --no-inc-recursive xk@10400:/home/xk/lb/$db.db sshfs_$db.db
    end
end
