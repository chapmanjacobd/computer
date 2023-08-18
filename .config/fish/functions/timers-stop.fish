# Defined interactively
function timers-stop
    ~/.config/systemd/user/
    systemctl --user disable --now *.timer
end
