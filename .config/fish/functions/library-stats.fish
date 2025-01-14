# Defined in /home/xk/.config/fish/functions/library-stats.fish @ line 2
function library-stats
    for db in ~/lb/fs/tax.db ~/lb/fs/video.db
        echo $db
        lb-dev wt $db -p a
        echo $db deleted
        lb-dev wt $db -w time_deleted'>'0 -p a
    end

    for db in ~/lb/fs/tax_sounds.db ~/lb/fs/audio.db
        echo $db
        lb-dev lt $db -p a
        echo $db deleted
        lb-dev lt $db -w time_deleted'>'0 -p a
        echo $db played
        lb-dev lt $db -w play_count'>'0 -p a
    end

    echo bigdirs
    for db in ~/lb/fs/tax.db ~/lb/fs/video.db ~/lb/fs/tax_sounds.db ~/lb/fs/audio.db
        echo $db
        lb-dev bigdirs $db -L 5
    end

    links-status ~/mc/cine.db ~/mc/links.db ~/mc/music.db ~/mc/tv.db ~/lb/sites/manual/*.db
    dlstatus ~/lb/fs/tax_sounds.db ~/lb/fs/video.db ~/lb/fs/tax.db ~/lb/fs/91_New_Art.db ~/lb/audio.db ~/lb/fs/61_Photos_Unsorted.db
end
