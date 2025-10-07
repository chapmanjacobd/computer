# Defined in /home/xk/.config/fish/functions/library-stats.fish @ line 2
function library-stats
    for db in ~/lb/fs/tax.db ~/lb/fs/video.db
        echo $db
        lb wt $db -p a
        echo $db deleted
        lb wt $db -w time_deleted'>'0 -p a
    end

    for db in ~/lb/fs/tax_sounds.db ~/lb/fs/audio.db
        echo $db
        lb lt $db -p a
        echo $db deleted
        lb lt $db -w time_deleted'>'0 -p a
        echo $db played
        lb lt $db -w play_count'>'0 -p a
    end

    echo bigdirs
    for db in ~/lb/fs/tax.db ~/lb/fs/video.db ~/lb/fs/tax_sounds.db ~/lb/fs/audio.db
        echo $db
        lb bigdirs $db -L 5
    end

    links-status ~/mc/cine.db ~/mc/links.db ~/mc/music.db ~/mc/tv.db ~/lb/sites/manual/*.db
    dlstatus ~/lb/dl/tax_sounds.db ~/lb/dl/video.db ~/lb/dl/tax.db ~/lb/dl/91_New_Art.db ~/lb/dl/audio.db ~/lb/dl/61_Photos_Unsorted.db
end
