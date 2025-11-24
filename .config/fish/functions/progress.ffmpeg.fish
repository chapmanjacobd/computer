# Defined interactively
function progress.ffmpeg
    for pid in (pgrep ffmpeg)
        progress -p $pid
    end
end
