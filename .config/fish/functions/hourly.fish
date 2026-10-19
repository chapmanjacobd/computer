# Defined interactively
function hourly
    priv.hourly

    torganize
    if test (uptime.seconds) -gt 3600; and not copying
        priv.allocate.torrents
    end
    torrents.maintenance
    qbt.unseed.old
end
