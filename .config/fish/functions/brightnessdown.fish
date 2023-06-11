# Defined interactively
function brightnessdown
    math (sudo ddcutil getvcp 10 | awk -F "=|," '/current value/ {print $2}' | string trim)-10
end
