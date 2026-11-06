# Defined interactively
function windows.maximize.all
    if test "$XDG_SESSION_TYPE" = wayland; and qdbus org.kde.KWin / >/dev/null 2>&1
        _windows.kwin maximize
        or return
    else
        for win in (windows | grep -iv plasma | cut -f1 -d' ')
            wmctrl -i -r $win -b toggle,maximized_horz,maximized_vert
            wmctrl -i -r $win -b add,maximized_horz,maximized_vert
        end
    end

    set is_enabled (kreadconfig6 --file kwinrc --group Plugins --key krohnkiteEnabled)
    if test "$is_enabled" = true
        krohnkite.off
        sleep 0.5
        krohnkite.on
    end
end
