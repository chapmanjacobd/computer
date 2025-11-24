# Defined interactively
function krohnkite.off
    kwriteconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled false
    qdbus org.kde.KWin /KWin reconfigure
end
