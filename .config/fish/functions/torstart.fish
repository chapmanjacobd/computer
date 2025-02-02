# Defined interactively
function torstart
    b lb computer-update computers.local.db
    b lb computer-update computers.remote.db
    wait

    lb allocate-torrents computers.local.db torrents.db -v --dl-limit 8Mi --up-limit 1.5Mi -E XXX pussytorrents.org plab.site bitporn.eu scenetime.com superbits.org exoticaz.to happyfappy.org empornium.is empornium.sx
    # lb allocate-torrents computers.remote.db torrents.db -v --dl-limit 8Mi --up-limit 1.5Mi --flex -s XXX pussytorrents.org plab.site bitporn.eu scenetime.com superbits.org exoticaz.to happyfappy.org empornium.is empornium.sx
end
