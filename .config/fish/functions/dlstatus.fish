function dlstatus
    echo audio.db
    lb-dev ds ~/lb/audio.db

    echo reddit/63_Sounds.db
    lb-dev ds ~/lb/reddit/63_Sounds.db --safe
    echo reddit/81_New_Music.db
    lb-dev ds ~/lb/reddit/81_New_Music.db --safe
    echo reddit/83_ClassicalComposers.db
    lb-dev ds ~/lb/reddit/83_ClassicalComposers.db --safe

    echo video.db
    lb-dev ds ~/lb/video.db
    echo reddit/71_Mealtime_Videos.db
    lb-dev ds ~/lb/reddit/71_Mealtime_Videos.db --safe
    echo hackernews/hackernews_only_direct.tw.db
    lb-dev ds ~/lb/hackernews/hackernews_only_direct.tw.db --safe
    echo fs/tax.db
    lb-dev ds ~/lb/fs/tax.db --safe
end
