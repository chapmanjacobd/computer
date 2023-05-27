# Defined interactively
function dlunsafe
    maxmem10b lb download ~/lb/reddit/63_Sounds.db --audio --prefix ~/d/63_Sounds/reddit/ $argv
    maxmem10b lb download ~/lb/reddit/81_New_Music.db --audio --prefix ~/d/81_New_Music/reddit/ $argv
    maxmem10b lb download ~/lb/reddit/83_ClassicalComposers.db --audio --prefix ~/d/83_ClassicalComposers/reddit/ $argv
    wait
    maxmem10b lb download ~/lb/reddit/71_Mealtime_Videos.db --video --small --prefix ~/d/71_Mealtime_Videos/reddit/ $argv
    maxmem10b lb download ~/lb/reddit/96_Weird_History.db --video --small --prefix ~/d/71_Mealtime_Videos/reddit/weird_history/ $argv
    wait
    maxmem10b lb download ~/lb/hackernews/hackernews_only_direct.tw.db --video --small --prefix ~/d/71_Mealtime_Videos/hn/ $argv
    maxmem10b lb download ~/lb/fs/tax.db -L 1000 --small --video --prefix /mnt/d/69_Taxes/ $argv
    maxmem10b lb download ~/lb/fs/61_Photos_Unsorted.db -L 1000 --small --video --prefix /mnt/d/69_Taxes/reddit/ $argv
end
