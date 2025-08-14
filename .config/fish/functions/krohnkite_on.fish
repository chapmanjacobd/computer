# Defined interactively
function krohnkite_on
    kwriteconfig5 --file kwinrc --group Plugins --key monocle_ultrawideEnabled true
    qdbus org.kde.KWin /KWin reconfigure
end
