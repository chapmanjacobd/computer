# Defined interactively
function brightness_lg_set
    pkill -f brightness_lg_set
    sudo modprobe i2c-dev && until.n 5 sudo ddcutil setvcp --mfg GSM 10 (math min 100,(math max 1,$argv))
end
