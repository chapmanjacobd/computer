# Defined via `source`
function focus_under_mouse
    kwriteconfig5 --file kwinrc --group Windows --key FocusPolicy FocusUnderMouse
    qdbus org.kde.KWin /KWin reconfigure
end
