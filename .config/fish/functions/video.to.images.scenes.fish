# Defined interactively
function video.to.scenes.images
    ffmpeg -i "$argv" -vf "select='gt(scene,0.3)'" -vsync vfr (path.withsuffix .%05d -e jpg "$argv")
end
