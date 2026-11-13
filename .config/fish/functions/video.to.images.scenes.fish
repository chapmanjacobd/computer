# Defined interactively
function video.to.scenes.images
    ffmpeg -i "$argv" -vf "select='gt(scene,0.3)'" -vsync vfr (path.withsuffix "$argv" .%05d jpg)
end
