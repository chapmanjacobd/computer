function forganize
    morganize
    dorganize

    set processing_dir processing_(datestamp)
    allpc library torrents --complete --seeders=+4 --time-stalled=+3days --time-active=+45days --stop --move $processing_dir --delete-rows -v
    # stop incomplete
    allpc library torrents --incomplete --time-unseeded=+90days --time-active=+60days --time-stalled=+30days --delete-incomplete --stop --move $processing_dir --delete-rows -v
    allpc library torrents --incomplete --time-active=+45days --inactive --progress=0 --stop -v

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
            yes | bfs -nohidden -type d -exec bfs -f {} -not -type d -exit 1 \; -prune -ok bfs -f {} -type d -delete \;
        end
    end
    mktree.py ~/d/

    # dsql_refresh
end
