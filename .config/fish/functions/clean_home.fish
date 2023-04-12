# Defined interactively
function clean_home
    ~/
    rmdir *
    trash-put .config/ksmserverrc .xsession-errors
    trash-put *.desktop
end
