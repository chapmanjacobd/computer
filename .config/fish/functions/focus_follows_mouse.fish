# Defined via `source`
function focus_follows_mouse
    kwriteconfig5 --file kwinrc --group Windows --key FocusPolicy FocusFollowsMouse
    kwriteconfig5 --file kwinrc --group Windows --key NextFocusPrefersMouse true
    qdbus-qt5 org.kde.KWin /KWin reconfigure
end
