# Defined interactively
function kwin.restart
    if test "$XDG_SESSION_TYPE" = x11
        kwin_x11 --replace & disown
    else
        qdbus org.kde.KWin /KWin reconfigure
    end
end
