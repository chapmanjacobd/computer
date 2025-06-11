# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    mam-promote (python -m library.scratch.mam_slots --max 4 --cookie $MAM_COOKIE)

    torganize
end
