# Defined interactively
function relax.video
    fish -c 'lb extract -f ~/lb/tax.db ~/sync/porn/video/ ~/sync/porn/image/ ~/d/check/porn/video/' &
    mpv --no-video --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/sync/porn/image) &
    lb wt ~/lb/tax.db -L inf --action ask_move_or_delete --keep-dir /home/xk/d/library/porn/video/ -m 2 $argv --sort "path like '%sync/porn/image%' desc, time_modified, duration desc, priority"
    pkill -x mpv
end
