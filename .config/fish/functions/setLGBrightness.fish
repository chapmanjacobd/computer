# Defined interactively
function setLGBrightness
    sudo modprobe i2c-dev && repeal sudo ddcutil setvcp 10 $argv
end
