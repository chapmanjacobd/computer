function forganize
    morganize.all
    dorganize

    lb.refresh
    lb.rebuild.fts

    lb.load
    yes | lb dedupe-media --fs ~/lb/fs/video.db -v
    yes | lb dedupe-media --fs ~/lb/fs/tax.db -v
    yes | lb dedupe-media --fs ~/lb/fs/audio.db -v

    ~/
    for dir in (nofs which -a /)*
        if test -d "$dir"
            "$dir"
            folders.empty.delete
        end
    end

    dsql.refresh.all
end
