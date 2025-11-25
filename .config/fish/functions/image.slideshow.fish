function image.slideshow
    feh --borderless --recursive --randomize --action "mv '%f' ../97_Inspiration" --action1 "mv '%f' ../97_Inspiration/" --action2 "mv '%f' ../95_Memes/" --action3 "mv '%f' ../96_Weird_History/" --action4 "mv '%f' ../dump/image/other/" --action5 "mv '%f' ../dump/image/other/" --action9 "/home/xk/.local/bin/trash '%f'" -G --auto-zoom --zoom max --draw-tinted --image-bg black --keep-zoom-vp --scale-down --slideshow-delay 2 --sort mtime $argv
end
