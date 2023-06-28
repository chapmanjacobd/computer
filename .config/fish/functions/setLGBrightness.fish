# Defined interactively
function setLGBrightness
    pkill -f setLGBrightness
    sudo modprobe i2c-dev && repeal sudo ddcutil setvcp --mfg GSM 10 $argv
end
