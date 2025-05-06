# Defined interactively
function reboot
    if not pgrep -fa ffmpeg
        sudo systemctl reboot
    end
end
