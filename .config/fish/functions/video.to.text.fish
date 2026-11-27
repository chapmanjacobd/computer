# Defined interactively
function video.to.text --wraps='ffmpeg'
    ffmpeg -i $argv -map 0:s:0 -f srt -
end
