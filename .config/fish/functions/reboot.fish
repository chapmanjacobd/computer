# Defined interactively
function reboot
    if not pgrep -fa ffmpeg
        sudo reboot
    end

end
