# Defined interactively
function timers-start
    timers.reset
    ~/.config/systemd/user/
    systemctl --user enable --now *.timer
end
