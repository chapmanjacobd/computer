# Defined interactively
function krohnkite_toggle
    set is_enabled (kreadconfig5 --file kwinrc --group Plugins --key monocle_ultrawideEnabled)

    if test "$is_enabled" = true
        kwriteconfig5 --file kwinrc --group Plugins --key monocle_ultrawideEnabled false
        echo "Krohnkite has been disabled."
    else
        kwriteconfig5 --file kwinrc --group Plugins --key monocle_ultrawideEnabled true
        echo "Krohnkite has been enabled."
    end

    qdbus org.kde.KWin /KWin reconfigure
end
