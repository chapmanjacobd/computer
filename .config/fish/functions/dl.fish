# Defined interactively
function dl
    lb download ~/lb/yt/podcasts.tl.db --audio --prefix ~/d/82_Audiobooks/
    lb download ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/
    lb download ~/lb/reddit/63_Sounds.db --audio --safe --prefix ~/d/63_Sounds/
    lb download ~/lb/reddit/81_New_Music.db --audio --safe --prefix ~/d/81_New_Music/
    lb download ~/lb/yt/classical_music.tl.db --audio --prefix ~/d/83_ClassicalComposers/
    lb download ~/lb/reddit/83_ClassicalComposers.db --audio --safe --prefix ~/d/83_ClassicalComposers/

    lb download ~/lb/video.db --video --small --prefix /mnt/d/71_Mealtime_Videos/
    lb download ~/lb/reddit/71_Mealtime_Videos.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/
    lb download ~/lb/hackernews/hackernews_only_direct.tw.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/
    library download ~/lb/fs/tax.db --safe --small --video --prefix /mnt/d/69_Taxes/
end
