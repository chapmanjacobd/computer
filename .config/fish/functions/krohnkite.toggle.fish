# Defined interactively
function krohnkite.toggle
    set is_enabled (kreadconfig6 --file kwinrc --group Plugins --key krohnkiteEnabled)

    if test "$is_enabled" = true
        kwriteconfig6 --file kwinrc --group Plugins --key krohnkiteEnabled false
        echo "Krohnkite has been disabled."
    else
        kwriteconfig6 --file kwinrc --group Plugins --key krohnkiteEnabled true
        echo "Krohnkite has been enabled."
    end

    qdbus org.kde.KWin /KWin reconfigure
end
