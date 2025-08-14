# Defined interactively
function krohnkite_off
    kwriteconfig5 --file kwinrc --group Plugins --key monocle_ultrawideEnabled false
    qdbus org.kde.KWin /KWin reconfigure
end
