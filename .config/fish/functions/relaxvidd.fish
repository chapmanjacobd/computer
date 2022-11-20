function relaxvidd
    fish -c 'lb extract ~/lb/fs/tax.db ~/d/60_Now_Watching/ ~/d/64_Relaxation/' &
    mpv --input-ipc-server=/tmp/mpv_socket --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/64_Relaxation) &
    mount_10400d
    lb-dev wt ~/lb/sshfs_tax.db -L inf --action askkeep --keep-dir /mnt/d/60_Now_Watching/keep/ --sort "path like '%64_Relaxation%' desc, time_modified, duration desc, priority" -m 3 $argv
    pkill -x mpv
end
