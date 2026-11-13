# Defined interactively
function video.to.scenes
    ffmpeg -i "$argv" -an -sn -filter:v "select='gt(scene,0.3)',setpts=N/FRAME_RATE/TB" (path.withsuffix .scenes -e mkv "$argv")
end
