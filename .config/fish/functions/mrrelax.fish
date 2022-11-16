function mrrelax
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/d/64_Relaxation/keep/ ~/d/62_Photos_Keep/

    fd --max-results=50 -tf . ~/d/61_Photos_Unsorted/ -0 | xargs -0 -I{} mv "{}" ~/d/64_Relaxation/

    fd --max-results=50 -tf . ~/d/91_New_Art/ -0 | xargs -0 -I{} mv "{}" ~/d/90_Now_Viewing/

    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --files-from=(
        lt ~/lb/63_Sounds.db -s /mnt/d/64_Relaxation/ -p f --moved /mnt/d/64_Relaxation/ /mnt/d/ | psub
    ) /mnt/d/64_Relaxation/ /mnt/d/

    rsync -a --remove-source-files --files-from=(
        lt ~/lb/63_Sounds.db -L 24 -p wf --moved /mnt/d/ /mnt/d/64_Relaxation/ | psub
    ) /mnt/d/ /mnt/d/64_Relaxation/

    lb fsadd --video ~/lb/fs/tax.db /mnt/d/64_Relaxation/

end
