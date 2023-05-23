# Defined interactively
function dla
    maxmem10b lb download ~/lb/yt/podcasts.tl.db --audio --prefix ~/d/82_Audiobooks/
    maxmem10b lb download ~/lb/reddit/63_Sounds.db --audio --safe --prefix ~/d/63_Sounds/reddit/
    maxmem10b lb download ~/lb/reddit/81_New_Music.db --audio --safe --prefix ~/d/81_New_Music/reddit/
    wait
    maxmem10b lb download ~/lb/yt/classical_music.tl.db --audio --prefix ~/d/83_ClassicalComposers/yt/
    maxmem10b lb download ~/lb/reddit/83_ClassicalComposers.db --audio --safe --prefix ~/d/83_ClassicalComposers/reddit/
    maxmem10b lb download ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/
    wait
    maxmem10b lb download ~/lb/video.db --video --small --prefix /mnt/d/71_Mealtime_Videos/
    maxmem10b lb download ~/lb/reddit/71_Mealtime_Videos.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/reddit/
    maxmem10b lb download ~/lb/reddit/96_Weird_History.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/reddit/weird_history/
    maxmem10b lb download ~/lb/reddit/95_Memes.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/reddit/memes/
    wait
    maxmem10b lb download ~/lb/hackernews/hackernews_only_direct.tw.db --video --small --safe --prefix ~/d/71_Mealtime_Videos/hn/
    maxmem10b lb download ~/lb/fs/tax.db -L 1000 --safe --small --video --prefix /mnt/d/69_Taxes/
    maxmem10b lb download ~/lb/fs/61_Photos_Unsorted.db -L 1000 --safe --small --video --prefix /mnt/d/69_Taxes/reddit/
    wait
end
