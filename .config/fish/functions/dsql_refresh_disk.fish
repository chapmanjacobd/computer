# Defined interactively
function dsql_refresh_disk
    set -l name (path basename $argv)

    set joblog (mktemp)
    for m in $argv/*
        echo lb fsadd --filesystem ~/disks/$name.db "$m"
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1
end
