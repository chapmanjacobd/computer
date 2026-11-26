# Defined interactively
function kwin.restart
    if not _is_wayland
        kwin_x11 --replace & disown
    else
        qdbus org.kde.KWin /KWin reconfigure
    end
end
