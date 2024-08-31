# Defined interactively
function ffvcs
    ffmpeg -i $argv -vf "select='gt(scene,0.4)',scale=1920:1080,tile" -vsync vfr output_%03d.jpg
end
