# Defined interactively
function d.sql.refresh
    set joblog (mktemp)
    for i in (seq 1 $MERGERFS_DISKS)
        for m in /mnt/d$i/*
            echo lb fsadd --filesystem ~/disks/d$i.db "$m"
        end
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1
end
