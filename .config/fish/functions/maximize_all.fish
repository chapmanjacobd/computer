# Defined interactively
function maximize_all
    for win in (lswin | grep -iv plasma | cut -f1 -d' ')
        wmctrl -i -r $win -b toggle,maximized_horz,maximized_vert
        wmctrl -i -r $win -b add,maximized_horz,maximized_vert
    end

    krohnkite_off
    sleep 0.5
    krohnkite_on
end
