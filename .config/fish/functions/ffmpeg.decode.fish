# Defined interactively
function ffmpeg.decode --wraps='ffmpeg'
    ffmpeg -v error -i $argv -f null -
end
