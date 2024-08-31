# Defined interactively
function ffmpeg.keyframes.images
    ffmpeg -i "$argv" -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr (path change-extension .%05d.jpg "$argv")
end
