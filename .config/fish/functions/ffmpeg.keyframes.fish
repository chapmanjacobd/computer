# Defined interactively
function ffmpeg.keyframes
    ffmpeg -discard nokey -i $argv -c copy /tmp/t1.264
    ffmpeg -r 30 -i /tmp/t1.264 -c copy (path change-extension .keys.mkv $argv)
end
