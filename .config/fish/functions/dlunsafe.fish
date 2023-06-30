# Defined interactively
function dlunsafe
    maxmem10b lbdl ~/lb/fs/63_Sounds.db --audio --prefix /mnt/d/63_Sounds/ $argv
    maxmem10b lbdl ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/ $argv
    wait
    maxmem10b lbdl ~/lb/video.db --video --small --prefix /mnt/d/71_Mealtime_Videos/ $argv
    wait
    maxmem10b lbdl ~/lb/fs/tax.db --video --small --prefix /mnt/d/69_Taxes/ $argv
    repeat sleepy_run.py -T (minutes 25) -t '429 Unknown' -- python -u -m xklb.lb dl --image --photos ~/lb/fs/61_Photos_Unsorted.db --prefix ~/d/61_Photos_Unsorted/gallery-dl/ $argv
    repeat sleepy_run.py -T (minutes 25) -t '429 Unknown' -- python -u -m xklb.lb dl --image --photos ~/lb/fs/91_New_Art.db --image --photos --prefix /mnt/d/91_New_Art/ $argv
    wait
end
