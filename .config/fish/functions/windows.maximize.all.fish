# Defined interactively
function windows.maximize.all
    for win in (lswin | grep -iv plasma | cut -f1 -d' ')
        wmctrl -i -r $win -b toggle,maximized_horz,maximized_vert
        wmctrl -i -r $win -b add,maximized_horz,maximized_vert
    end

    set is_enabled (kreadconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled)
    if test "$is_enabled" = true
        krohnkite.off
        sleep 0.5
        krohnkite_on
    end
end
