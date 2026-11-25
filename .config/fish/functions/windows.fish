# Defined interactively
function windows
    if test "$XDG_SESSION_TYPE" = wayland; and qdbus org.kde.KWin / >/dev/null 2>&1
        _windows.kwin list | column -t -s \t
        return
    end

    wmctrl -G -l | awk -v OFS='\t' '{print $1, $2","$3","$4","$5","$6, substr($0, index($0,$7))}' | column -t -s \t
end
