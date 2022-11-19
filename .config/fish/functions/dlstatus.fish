# Defined interactively
function dlstatus
    for db in ~/lb/audio.db ~/lb/yt/podcasts.tl.db ~/lb/reddit/63_Sounds.db ~/lb/hackernews/hackernews_only_direct.tw.db ~/lb/reddit/81_New_Music.db ~/lb/yt/classical_music.tl.db ~/lb/reddit/83_ClassicalComposers.db ~/lb/video.db ~/lb/reddit/71_Mealtime_Videos.db
        echo $db
        lb ds $db
    end
end
