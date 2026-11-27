# Defined interactively
function video.to.keyframes --wraps='ffmpeg'
    ffmpeg -i "$argv" -c copy -bsf:v 'noise=drop=not(key)' (path.withsuffix .quickkeys -e mkv "$argv")
end
