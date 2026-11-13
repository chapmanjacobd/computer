# Defined interactively
function video.shrink.audio
    ffmpeg -i "$argv" -c:a libopus -ab 32k -ar 22050 -ac 1 (path.withsuffix "$argv" .small opus)
end
