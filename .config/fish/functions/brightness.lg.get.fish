# Defined interactively
function brightness.lg.get
    sudo ddcutil getvcp --mfg GSM 10 | awk -F "=|," '/current value/ {print $2}' | string trim
end
