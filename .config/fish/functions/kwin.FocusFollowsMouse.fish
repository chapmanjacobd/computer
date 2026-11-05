# Defined via `source`
function kwin.FocusFollowsMouse
    kwriteconfig6 --file kwinrc --group Windows --key FocusPolicy FocusFollowsMouse
    kwriteconfig6 --file kwinrc --group Windows --key NextFocusPrefersMouse true
    qdbus org.kde.KWin /KWin reconfigure
end
