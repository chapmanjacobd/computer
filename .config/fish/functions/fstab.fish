# Defined interactively
function fstab
    sudo nano /etc/fstab
    cp /etc/fstab ~/.github/etc/
    sudo systemctl daemon-reload
end
