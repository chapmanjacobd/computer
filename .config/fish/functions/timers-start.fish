# Defined interactively
function timers-start
    ~/.config/systemd/user/
    systemctl --user enable --now *.timer
end
