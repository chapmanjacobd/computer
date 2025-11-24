function relax.video.multi
    fish -c 'lb extract ~/lb/tax.db ~/sync/porn/video/ ~/sync/porn/image/' &
    mpv --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/sync/porn/image) &
    mount_pakond
    lb wt ~/lb/sshfs_tax.db -L inf --action ask_move_or_delete --keep-dir /mnt/d/library/porn/video/ --sort "path like '%sync/porn/image%' desc, time_modified, duration desc, priority" -m 3 $argv
    pkill -x mpv
end
