# Defined interactively
function video.to.keyframes
    ffmpeg -i "$argv" -c copy -bsf:v 'noise=drop=not(key)' (path change-extension .quickkeys.mkv "$argv")
end
