function relaxvidd
    fish -c 'lb extract ~/lb/tax.db ~/d/sync/porn/video/ ~/d/sync/porn/image/' &
    mpv --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/sync/porn/image) &
    mount_pakond
    lb-dev wt ~/lb/sshfs_tax.db -L inf --action ask_move_or_delete --keep-dir /mnt/d/library/porn/video/ --sort "path like '%sync/porn/image%' desc, time_modified, duration desc, priority" -m 3 $argv
    pkill -x mpv
end
