# Defined interactively
function reboot
    progress -wc ffmpeg
    if test $status -ne 0
        sudo reboot
    end

end
