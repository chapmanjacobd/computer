# Defined interactively
function clean_home
    ~/
    rmdir * 2>/dev/null
    trash-put .config/ksmserverrc .xsession-errors 2>/dev/null
    fd -d1 -tf -eDESKTOP -x trash
    fd -d2 -tf -H '.syncthing.*.tmp' -x trash

    git add .
    and git pull
    and git reset
end
