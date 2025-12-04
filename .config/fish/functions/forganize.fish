function forganize
    morganize.all
    dorganize

    lb.refresh
    lb.rebuild.fts

    lb.load
    yes | lb dedupe-media --fs ~/lb/fs/video.db -v
    yes | lb dedupe-media --fs ~/lb/fs/tax.db -v
    yes | lb dedupe-media --fs ~/lb/fs/audio.db -v

    ~/d/
    for dir in /mnt/d(seq 1 $MERGERFS_DISKS)/*
        if test -d "$dir"
            "$dir"
            folders.empty.delete
        end
    end
    mktree.py ~/d/

    d.sql.refresh
end
