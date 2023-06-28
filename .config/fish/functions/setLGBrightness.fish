# Defined interactively
function setLGBrightness
    sudo pkill ddcutil
    sudo modprobe i2c-dev && repeal sudo ddcutil setvcp --mfg GSM 10 $argv
end
