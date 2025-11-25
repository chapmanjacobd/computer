# Defined interactively
function timers.stop
    ~/.config/systemd/user/
    systemctl --user disable --now *.timer
    systemctl --user enable --now daily.timer weekly.timer monthly.timer
end
