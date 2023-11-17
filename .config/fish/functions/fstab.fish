# Defined interactively
function fstab
    sudo nano /etc/fstab
    cp /etc/fstab ~/.github/etc/
    systemctl daemon-reload
end
