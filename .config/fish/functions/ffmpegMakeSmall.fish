# Defined interactively
function ffmpegMakeSmall
    set filen (string split -r -m1 . "$argv[1]")[1]
    ffmpeg -hide_banner -y -i "$argv[1]" $argv[2..-1] -map 0 -vf "scale=-2:min(ih\,1440)" -vcodec libx265 -preset 4 -acodec libopus -b:a 96k -vbr constrained "$filen".small.mkv && /bin/rm "$argv[1]"
end
