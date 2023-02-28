# Defined in /home/xk/.config/fish/functions/library-stats.fish @ line 2
function library-stats
    for db in ~/lb/fs/61_Photos_Unsorted.db ~/lb/fs/tax.db ~/lb/video.db
        echo $db
        lb-dev wt $db -p a
        echo $db deleted
        lb-dev wt $db -w time_deleted'>'0 -p a
    end

    for db in ~/lb/fs/63_Sounds.db ~/lb/audio.db
        echo $db
        lb-dev lt $db -p a
        echo $db deleted
        lb-dev lt $db -w time_deleted'>'0 -p a
        echo $db played
        lb-dev lt $db -w play_count'>'0 -p a
    end

    echo bigdirs
    for db in ~/lb/fs/61_Photos_Unsorted.db ~/lb/fs/tax.db ~/lb/video.db ~/lb/fs/63_Sounds.db ~/lb/audio.db
        echo $db
        lb-dev bigdirs $db -L 5
    end

end
