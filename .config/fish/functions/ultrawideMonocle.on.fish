# Defined interactively
function ultrawideMonocle.on
    kwriteconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled true
    qdbus org.kde.KWin /KWin reconfigure
end
