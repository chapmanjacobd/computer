function forganize
    morganize
    dorganize

    qbt-unseed

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
    #lb wt ~/lb/fs/tax.db -l inf --local-media-only -d-0.8 --keep-dir /mnt/d/check/porn/video/ -pf | xargs -P 20 -I{} rm {}
    #lb wt ~/lb/fs/tax.db -l inf --local-media-only -d-0.8 -pfd

    # ~/d/dump/audio/midi/ && fd -tf -eMID -x mv "{}" "{.}.mid"

    # fd . ~/d/dump/porn/audio/ ~/d/dump/audio/ -epng -ejpg -x rm "{}"

    lb-load
    yes | lb dedupe-media --fs ~/lb/fs/video.db -v --dedupe-cmd dupreplace.fish
    yes | lb dedupe-media --fs ~/lb/fs/tax.db -v
    yes | lb dedupe-media --fs ~/lb/fs/audio.db -v

    ~/d/
    for dir in /mnt/d(seq 1 $MERGERFS_DISKS)/*
        if test -d "$dir"
            "$dir"
            remove_empty_directories
        end
    end
    mktree.py ~/d/

    dsql_refresh
end
