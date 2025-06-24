# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    mam-promote (python ~/bin/mam_slots.py --max 5 --cookie $MAM_COOKIE)

    torganize
end
