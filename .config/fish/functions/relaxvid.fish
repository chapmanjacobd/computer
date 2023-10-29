# Defined interactively
function relaxvid
    fish -c 'lb extract -f ~/lb/fs/tax.db ~/d/60_Now_Watching/ ~/d/64_Relaxation/ ~/d/69_Taxes_Keep/' &
    mpv --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/64_Relaxation) &
    lb-dev wt ~/lb/fs/tax.db -L inf --action ask_move_or_delete --keep-dir /home/xk/d/69_Taxes_Keep/ -m 2 $argv --sort "path like '%64_Relaxation%' desc, time_modified, duration desc, priority"
    pkill -x mpv
end
