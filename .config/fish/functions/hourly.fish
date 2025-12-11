# Defined interactively
function hourly
    load.env.mam
    ~/bin/mam_upload_credit.sh

    mam.promote (mam_slots.py --max 10 --cookie $MAM_COOKIE)

    torganize
    if test (uptime.seconds) -gt 3600; and not copying
        priv.allocate.torrents
    end
    torrents.maintenance
    qbt.unseed.old
end
