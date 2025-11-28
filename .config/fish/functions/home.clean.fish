# Defined interactively
function home.clean
    ~/
    command rmdir * 2>/dev/null
    trash .config/ksmserverrc .xsession-errors .config/libaccounts-glib 2>/dev/null
    fd -d1 -tf -eDESKTOP -x trash
    fd -d2 -tf -H '.syncthing.*.tmp' -x trash

    git add .
    and git pull
    and git reset
end
