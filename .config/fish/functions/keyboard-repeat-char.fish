# Defined interactively
function keyboard-repeat-char
    xdotool key --repeat 99999 --delay 820 $argv
    sleep 1
    xdotool key $argv
end
