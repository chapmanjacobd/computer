# Defined interactively
function windows.minimize.all
    if test "$XDG_SESSION_TYPE" = wayland; and qdbus org.kde.KWin / >/dev/null 2>&1
        _windows.kwin unmaximize
        or return
    else
        for win in (windows | grep -iv plasma | cut -f1 -d' ')
            wmctrl -i -r $win -b toggle,maximized_horz,maximized_vert
            wmctrl -i -r $win -b remove,maximized_horz,maximized_vert
        end
    end

    set is_enabled (kreadconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled)
    if test "$is_enabled" = true
        ultrawideMonocle.off
        sleep 0.5
        ultrawideMonocle.on
    end
end
