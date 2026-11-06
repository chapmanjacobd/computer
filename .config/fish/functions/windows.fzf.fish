# Defined interactively
function windows.fzf
    if test "$XDG_SESSION_TYPE" = wayland; and qdbus org.kde.KWin / >/dev/null 2>&1
        _windows.kwin list | fzf | cut -f1
        return $pipestatus[1]
    end

    wmctrl -l -x | grep -v plasmashell.plasmashell | fzf | cut -f1 -d' '
end
