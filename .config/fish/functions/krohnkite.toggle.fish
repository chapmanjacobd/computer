# Defined interactively
function krohnkite.toggle
    set is_enabled (kreadconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled)

    if test "$is_enabled" = true
        kwriteconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled false
        echo "Krohnkite has been disabled."
    else
        kwriteconfig5 --file kwinrc --group Plugins --key krohnkiteEnabled true
        echo "Krohnkite has been enabled."
    end

    qdbus org.kde.KWin /KWin reconfigure
end
