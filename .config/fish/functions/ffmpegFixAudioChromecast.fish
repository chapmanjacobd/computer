# Defined via `source`
function ffmpegFixAudioChromecast --wraps=ffmpeg
    set out (random-filename "$argv[1]")
    ffmpeg -nostdin -loglevel error -stats -i "$argv[1]" -map 0 -scodec webvtt -vcodec h264 -preset fast -profile:v high -level 4.1 -crf 17 -pix_fmt yuv420p -acodec opus -ac 2 -b:a 128k -filter:a loudnorm=i=-18:lra=17 $argv[2..-1] $out
    echo $out
end
