# Defined interactively
function krohnkite_on
    kwriteconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled true
    qdbus org.kde.KWin /KWin reconfigure
end
