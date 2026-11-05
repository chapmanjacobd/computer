# Defined interactively
function krohnkite.on
    kwriteconfig6 --file kwinrc --group Plugins --key krohnkiteEnabled true
    qdbus org.kde.KWin /KWin reconfigure
end
