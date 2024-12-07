function forganize
    morganize
    dorganize

    allpc library torrents-stop-incomplete --min-days-downloading 20 --move processing --delete-rows -y -v
    allpc library torrents-stop --min-seeders 3 --min-days-stalled-seed 3 --min-days-seeding 45 --move processing --delete-rows -y -v

    #trash-size
    #trash-empty

    #ulimit -n 10240
    #set joblog (mktemp)
    #for m in /mnt/d(seq 1 $MERGERFS_DISKS)/*
    #    if string match -qv -- '*Seeding*' "$m"
    #        echo library christen -r "$m" -v
    #    end
    #end | parallel --shuf --joblog $joblog
    #parallel --retry-failed --joblog $joblog -j1

    fd -tf -d1 --fixed-strings ? . (cat d/.stignore | grep !/ | sed 's|!/\(.*\)|/home/xk/d/\1/|') -x rename ? '' {}

    lb-refresh
    lb-rebuild-fts
    #lb wt ~/lb/tax.db -l inf --local-media-only -d-0.8 --keep-dir /mnt/d/check/porn/video/ -pf | xargs -P 20 -I{} rm {}
    #lb wt ~/lb/tax.db -l inf --local-media-only -d-0.8 -pfd

    # ~/d/dump/audio/midi/ && fd -tf -eMID -x mv "{}" "{.}.mid"

    # fd . ~/d/dump/porn/audio/ ~/d/dump/audio/ -epng -ejpg -x rm "{}"

    lb-load
    yes | lb dedupe-media --fs ~/lb/video.db -v --dedupe-cmd dupreplace.fish
    yes | lb dedupe-media --fs ~/lb/tax.db -v
    yes | lb dedupe-media --fs ~/lb/audio.db -v

    ~/d/
    for dir in /mnt/d(seq 1 $MERGERFS_DISKS)/*
        if test -d "$dir"
            "$dir"
            yes | bfs -nohidden -type d -exec bfs -f {} -not -type d -exit 1 \; -prune -ok bfs -f {} -type d -delete \;
        end
    end
    mktree.py ~/d/

    dsql_refresh
end
