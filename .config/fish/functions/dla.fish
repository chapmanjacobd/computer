# Defined interactively
function dla
    b lb download ~/lb/yt/podcasts.tl.db --audio --prefix ~/d/82_Audiobooks/
    b lb download ~/lb/reddit/63_Sounds.db --audio --safe --prefix ~/d/63_Sounds/reddit/
    b lb download ~/lb/reddit/81_New_Music.db --audio --safe --prefix ~/d/81_New_Music/reddit/
    b lb download ~/lb/yt/classical_music.tl.db --audio --prefix ~/d/83_ClassicalComposers/yt/
    b lb download ~/lb/reddit/83_ClassicalComposers.db --audio --safe --prefix ~/d/83_ClassicalComposers/reddit/
    b lb download ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/

    b lb download ~/lb/video.db --video --small --prefix /mnt/d/71_Mealtime_Videos/
    b lb download ~/lb/reddit/71_Mealtime_Videos.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/reddit/
    b lb download ~/lb/hackernews/hackernews_only_direct.tw.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/hn/
    b lb download ~/lb/fs/tax.db --safe --small --video --prefix /mnt/d/69_Taxes/
end
