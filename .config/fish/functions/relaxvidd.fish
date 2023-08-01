function relaxvidd
    fish -c 'lb extract ~/lb/fs/tax.db ~/d/60_Now_Watching/ ~/d/64_Relaxation/' &
    mpv --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/64_Relaxation) &
    mount_pakond
    lb-dev wt ~/lb/sshfs_tax.db -L inf --action ask_move_or_delete --keep-dir /mnt/d/60_Now_Watching/keep/ --sort "path like '%64_Relaxation%' desc, time_modified, duration desc, priority" -m 3 $argv
    pkill -x mpv
end
