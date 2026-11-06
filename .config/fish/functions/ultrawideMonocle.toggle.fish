# Defined interactively
function ultrawideMonocle.toggle
    set is_enabled (kreadconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled)

    if test "$is_enabled" = true
        kwriteconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled false
        echo "Monocle ultrawide has been disabled."
    else
        kwriteconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled true
        echo "Monocle ultrawide has been enabled."
    end

    qdbus org.kde.KWin /KWin reconfigure
end
