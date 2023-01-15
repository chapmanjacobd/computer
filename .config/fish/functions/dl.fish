# Defined interactively
function dl
    echo audio.db
    lb download ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/
    echo yt/podcasts.tl.db
    lb download ~/lb/yt/podcasts.tl.db --audio --prefix ~/d/82_Audiobooks/
    echo yt/classical_music.tl.db
    lb download ~/lb/yt/classical_music.tl.db --audio --prefix ~/d/83_ClassicalComposers/

    echo reddit/63_Sounds.db
    lb download ~/lb/reddit/63_Sounds.db --audio --safe --prefix ~/d/63_Sounds/
    echo reddit/81_New_Music.db
    lb download ~/lb/reddit/81_New_Music.db --audio --safe --prefix ~/d/81_New_Music/
    echo reddit/83_ClassicalComposers.db
    lb download ~/lb/reddit/83_ClassicalComposers.db --audio --safe --prefix ~/d/83_ClassicalComposers/

    echo video.db
    lb download ~/lb/video.db --video --small --prefix /mnt/d/71_Mealtime_Videos/
    echo reddit/71_Mealtime_Videos.db
    lb download ~/lb/reddit/71_Mealtime_Videos.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/
    echo hackernews/hackernews_only_direct.tw.db
    lb download ~/lb/hackernews/hackernews_only_direct.tw.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/
    echo fs/tax.db
    lb download ~/lb/fs/tax.db --safe --small --video --prefix /mnt/d/69_Taxes/
end
