function forganize
    morganize
    dorganize

    qbt-unseed

    lb-refresh
    lb-rebuild-fts

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
