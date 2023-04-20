# Defined interactively
function ffmpegToChromecast --wraps=ffmpeg
    for file in $argv
        ffmpeg -nostdin -loglevel error -stats -i "$file" -map 0 -scodec webvtt -vcodec h264 -preset fast -profile:v high -level 4.1 -crf 17 -pix_fmt yuv420p -acodec opus -ac 2 -b:a 128k -filter:a loudnorm=i=-18:lra=17 (random-filename "$file")
    end
end
