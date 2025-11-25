# Defined interactively
function home.clean.permissions
    find /home/$USER ! -user $USER
    sudo restorecon -rv .
end
