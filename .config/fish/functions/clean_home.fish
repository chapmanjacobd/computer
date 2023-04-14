# Defined interactively
function clean_home
    ~/
    rmdir *
    trash-put .config/ksmserverrc .xsession-errors
    trash-put *.desktop
    git add .
    git pull
    git reset
end
