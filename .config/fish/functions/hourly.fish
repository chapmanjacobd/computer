# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    mam-promote (mam_slots.py --max 5 --cookie $MAM_COOKIE)

    torganize
    priv-allocate-torrents
    torrent-maintenance
    qbt-unseed
end
