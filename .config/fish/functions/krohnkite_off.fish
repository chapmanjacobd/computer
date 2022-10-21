# Defined interactively
function krohnkite_off
    kwriteconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled false
    qdbus-qt5 org.kde.KWin /KWin reconfigure
end
