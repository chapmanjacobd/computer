# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    mam-promote (mam_slots.py --max 5 --cookie $MAM_COOKIE)

    if test (uptime_secs) -gt 3600; and not pgrep -fa torrents
        torganize
        priv-allocate-torrents
        torrent-maintenance
        qbt-unseed
    end
end
