# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    mam-promote (mam_slots.py --max 5 --cookie $MAM_COOKIE)

    torganize
    if test (uptime_secs) -gt 3600; and not copying
        priv-allocate-torrents
    end
    torrent-maintenance
    qbt-unseed
    lb-dev torrents --dl --no-fast --no-queued --no-stopped --force-start
end
