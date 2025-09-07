# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    mam-promote (mam_slots.py --max 5 --cookie $MAM_COOKIE)

    torganize
    if test (uptime_secs) -gt 3600; and not pgrep -fa torrents; and not pgrep -a mv; and not pgrep -fa 'lb mv'; and not pgrep -a rsync
        priv-allocate-torrents
    end
    torrent-maintenance
    qbt-unseed
end
