function relaxvidd
    fish -c 'lb extract ~/lb/fs/tax.db ~/d/sync/porn/video/ ~/d/sync/porn/image/' &
    mpv --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/64_Relaxation) &
    mount_pakond
    lb-dev wt ~/lb/sshfs_tax.db -L inf --action ask_move_or_delete --keep-dir /mnt/d/archive/porn/video/ --sort "path like '%64_Relaxation%' desc, time_modified, duration desc, priority" -m 3 $argv
    pkill -x mpv
end
