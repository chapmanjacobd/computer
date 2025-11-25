# Defined interactively
function timers.reset
    touch ~/.local/share/systemd/timers/stamp*.timer
    find ~/.config/systemd/user/*.wants/ -xtype l -delete
end
