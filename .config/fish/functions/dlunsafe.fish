# Defined interactively
function dlunsafe
    run.b.mem10G lbdl ~/lb/dl/tax_sounds.db --audio --prefix /mnt/d/dump/porn/audio/ $argv
    run.b.mem10G lbdl ~/lb/dl/audio.db --audio --prefix /mnt/d/dump/audio/ $argv
    wait
    run.b.mem10G lbdl ~/lb/dl/video.db --video --small --prefix /mnt/d/dump/video/other/ $argv
    wait
    run.b.mem10G lbdl ~/lb/dl/tax.db --video --small --prefix /mnt/d/dump/porn/video/ $argv
    repeat sleepy_run.py -T (minutes 25) -t '429 Unknown' -- python -u -m library.lb dl --image --photos ~/lb/fs/61_Photos_Unsorted.db --prefix ~/d/dump/porn/image/gallery-dl/ $argv
    repeat sleepy_run.py -T (minutes 25) -t '429 Unknown' -- python -u -m library.lb dl --image --photos ~/lb/fs/91_New_Art.db --image --photos --prefix /mnt/d/dump/image/other/ $argv
    wait
end
