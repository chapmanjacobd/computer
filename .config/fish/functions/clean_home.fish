# Defined interactively
function clean_home
    ~/
    rmdir *
    trash-put .config/ksmserverrc .xsession-errors
end
