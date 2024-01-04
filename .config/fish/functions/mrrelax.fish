function mrrelax
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/d/sync/porn/image/keep/ ~/d/sync/porn/image/

    fd --max-results=500 -tf . ~/d/dump/porn/image/ -0 | xargs -0 -I{} mv "{}" ~/d/sync/porn/image/

    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --files-from=(
        lt --db ~/lb/fs/63_Sounds.db -s /mnt/d/sync/porn/image/ -p f --moved /mnt/d/sync/porn/image/ /mnt/d/ | psub
    ) /mnt/d/sync/porn/image/ /mnt/d/

    rsync -a --remove-source-files --files-from=(
        lt --db ~/lb/fs/63_Sounds.db -L 24 -p wf --moved /mnt/d/ /mnt/d/sync/porn/image/ | psub
    ) /mnt/d/ /mnt/d/sync/porn/image/

    lb fsadd --video ~/lb/fs/tax.db /mnt/d/sync/porn/image/

end
