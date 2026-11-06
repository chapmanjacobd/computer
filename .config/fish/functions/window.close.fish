# Defined interactively
function window.close
    if test "$XDG_SESSION_TYPE" = wayland; and qdbus org.kde.KWin / >/dev/null 2>&1
        set -l win (windows.fzf)
        if test -n "$win"
            _windows.kwin close "$win"
            return $status
        end
        return 0
    end

    wmctrl -c (windows.fzf)
end
