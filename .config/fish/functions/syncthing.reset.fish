# Defined interactively
function syncthing.reset
    syncthing cli operations shutdown
    syncthing debug reset-database
    sudo systemctl start syncthing@xk
end
