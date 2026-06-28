# Defined interactively
function dsql.refresh.remote
    for s in $servers
        ssh $s dsql.refresh.all
        rsync -ah --info=progress2 --no-inc-recursive --partial-dir=.rsync-partial $s:disks/ ~/disks/$s/
    end
end
