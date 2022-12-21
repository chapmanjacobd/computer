# Defined interactively
function shutdown
    progress -wc ffmpeg
    if test $status -ne 0
        sudo shutdown now
    end
end
