function relaxvid
    fish -c 'lb extract ~/lb/tax.db ~/d/60_Now_Watching/ ~/d/64_Relaxation/' &
    mpv --input-ipc-server=/tmp/mpv_socket --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/64_Relaxation) &
    lb-dev wt ~/lb/tax.db -L inf --action askkeep --keep-dir /home/xk/d/60_Now_Watching/keep/ --sort "path like '%64_Relaxation%' desc, time_modified, duration desc, priority" -m 3 $argv
    pkill -x mpv
end
