# Defined interactively
function keyboard-repeat-char
    xdotool key --repeat 9999999 --delay 180 $argv
    xdotool key $argv
end
