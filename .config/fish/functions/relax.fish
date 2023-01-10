# Defined via `source`
function relax
    fish -c 'lb extract ~/lb/fs/tax.db ~/d/60_Now_Watching/ ~/d/64_Relaxation/' &
    ~/d/64_Relaxation
    mpv --input-ipc-server=/tmp/mpv_socket --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/64_Relaxation) &
    feh -q -F --hide-pointer --sort filename --on-last-slide resume --action2 "mv '%f' ./keep/" --action1 "trash-put '%f'" --action3 "mv '%f' ../95_Memes/" --action4 "mv '%f' ../96_Weird_History/" --action5 "mv '%f' ../52_Receipts/" --action7 "mv '%f' ../94_Cool/" --action8 "mv '%f' ../93_BG/" --action6 "mv '%f' ../98_Me/" --action "trash-put '%f'" -G --auto-zoom --zoom max --draw-tinted --image-bg black --scale-down -D -3 .
    pkill mpv
end
