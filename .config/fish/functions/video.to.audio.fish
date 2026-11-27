# Defined interactively
function video.to.audio --wraps='ffmpeg'
    ffmpeg -i "$argv" -vn -y -c:a copy (path change-extension mka "$argv")
end
