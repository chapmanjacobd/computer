# Defined interactively
function clean_home_advanced
    find /home/$USER ! -user $USER
    sudo restorecon -rv .
end
