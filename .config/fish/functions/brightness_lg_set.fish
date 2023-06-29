# Defined interactively
function brightness_lg_set
    pkill -f brightness_lg_set
    sudo modprobe i2c-dev && repeal sudo ddcutil setvcp --mfg GSM 10 $argv
end
