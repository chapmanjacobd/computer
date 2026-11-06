# Defined interactively
function ultrawideMonocle.off
    kwriteconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled false
    qdbus org.kde.KWin /KWin reconfigure
end
