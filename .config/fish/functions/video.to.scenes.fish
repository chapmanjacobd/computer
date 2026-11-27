# Defined interactively
function video.to.scenes --wraps='ffmpeg'
    ffmpeg -i "$argv" -an -sn -filter:v "select='gt(scene,0.3)',setpts=N/FRAME_RATE/TB" (path.withsuffix .scenes -e mkv "$argv")
end
