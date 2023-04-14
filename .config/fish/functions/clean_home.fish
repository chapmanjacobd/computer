# Defined interactively
function clean_home
    ~/
    rmdir * 2>/dev/null
    trash-put .config/ksmserverrc .xsession-errors 2>/dev/null
    fd -d1 -tf -eDESKTOP -x rm

    git add .
    and git pull
    and git reset
end
