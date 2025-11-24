# Defined via `source`
function kwin.FocusUnderMouse
    kwriteconfig5 --file kwinrc --group Windows --key FocusPolicy FocusUnderMouse
    qdbus org.kde.KWin /KWin reconfigure
end
