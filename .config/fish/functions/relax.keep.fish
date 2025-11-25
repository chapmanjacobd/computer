# Defined via `source`
function relax.keep
    ~/sync/porn/image/keep/
    mpv --af="acompressor=ratio=4,loudnorm" (fd -eOPUS -eOGA -eWEBM . ~/sync/porn/image) &
    feh --hide-pointer --randomize --on-last-slide resume --action1 "/home/xk/.local/bin/trash '%f'" -G --auto-zoom --zoom max --draw-tinted --image-bg black --scale-down -D 2 .
    pkill mpv
end
