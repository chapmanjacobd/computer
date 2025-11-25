# Defined interactively
function windows.minimize.all
    for win in (windows | grep -iv plasma | cut -f1 -d' ')
        wmctrl -i -r $win -b toggle,maximized_horz,maximized_vert
        wmctrl -i -r $win -b remove,maximized_horz,maximized_vert
    end

    set is_enabled (kreadconfig5 --file kwinrc --group Plugins --key monocle_ultrawideEnabled)
    if test "$is_enabled" = true
        krohnkite.off
        sleep 0.5
        krohnkite.on
    end
end
