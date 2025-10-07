# Defined interactively
function dlunsafe
    maxmem10b lbdl ~/lb/fs/tax_sounds.db --audio --prefix /mnt/d/dump/porn/audio/ $argv
    maxmem10b lbdl ~/lb/fs/audio.db --audio --prefix /mnt/d/dump/audio/ $argv
    wait
    maxmem10b lbdl ~/lb/fs/video.db --video --small --prefix /mnt/d/dump/video/other/ $argv
    wait
    maxmem10b lbdl ~/lb/dl/tax.db --video --small --prefix /mnt/d/dump/porn/video/ $argv
    repeat sleepy_run.py -T (minutes 25) -t '429 Unknown' -- python -u -m library.lb dl --image --photos ~/lb/fs/61_Photos_Unsorted.db --prefix ~/d/dump/porn/image/gallery-dl/ $argv
    repeat sleepy_run.py -T (minutes 25) -t '429 Unknown' -- python -u -m library.lb dl --image --photos ~/lb/fs/91_New_Art.db --image --photos --prefix /mnt/d/dump/image/other/ $argv
    wait
end
