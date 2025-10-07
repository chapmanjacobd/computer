function mrrelax
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/sync/porn/image/keep/ ~/sync/porn/image/

    fd --max-results=500 -tf . ~/d/dump/porn/image/ -0 | xargs -0 -I{} mv "{}" ~/sync/porn/image/

    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --files-from=(
        lt --db ~/lb/fs/tax_sounds.db -s ~/sync/porn/image/ -p f --moved ~/sync/porn/image/ /mnt/d/ | psub
    ) ~/sync/porn/image/ /mnt/d/

    rsync -a --remove-source-files --files-from=(
        lt --db ~/lb/fs/tax_sounds.db -L 24 -p wf --moved /mnt/d/ ~/sync/porn/image/ | psub
    ) /mnt/d/ ~/sync/porn/image/

    lb fsadd --video ~/lb/tax.db ~/sync/porn/image/

end
