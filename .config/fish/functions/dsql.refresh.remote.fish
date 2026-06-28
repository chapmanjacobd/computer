# Defined interactively
function dsql.refresh.remote
    ssh $argv dsql.refresh.all
    rsync -ah --info=progress2 --no-inc-recursive --partial-dir=.rsync-partial $argv:disks/ ~/disks/$argv/
end
