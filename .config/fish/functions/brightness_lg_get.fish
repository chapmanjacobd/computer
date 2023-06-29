# Defined interactively
function brightness_lg_get
    sudo ddcutil getvcp --mfg GSM 10 | awk -F "=|," '/current value/ {print $2}' | string trim
end
