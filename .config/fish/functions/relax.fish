# Defined via `source`
function relax
    fish -c 'lb extract ~/lb/tax.db ~/d/sync/porn/video/ ~/d/sync/porn/image/' &
    ~/d/sync/porn/image
    mpv --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA . ~/d/sync/porn/image) &
    feh -q -F --hide-pointer --sort filename --on-last-slide resume --action2 "mv '%f' ./keep/" --action1 "trash-put '%f'" --action3 "mv '%f' ../95_Memes/" --action4 "mv '%f' ../96_Weird_History/" --action5 "mv '%f' ../dump/text/receipts/" --action7 "mv '%f' ../dump/image/other/" --action8 "mv '%f' ../dump/image/other/" --action6 "mv '%f' ../sync/self/portraits/" --action "trash-put '%f'" -G --auto-zoom --zoom max --draw-tinted --image-bg black --scale-down -D -3 .
    pkill mpv
end
