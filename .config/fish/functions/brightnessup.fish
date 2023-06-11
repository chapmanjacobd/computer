# Defined interactively
function brightnessup
    setLGBrightness (math (sudo ddcutil getvcp 10 | awk -F "=|," '/current value/ {print $2}' | string trim)+5)
end
