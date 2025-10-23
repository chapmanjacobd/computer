# Defined interactively
function wtseek
    focus_under_mouse
    b repeatdelay 0.7 xdotool key i
    set key_pid (jobs -lp)

    wt $argv

    kill $key_pid
    focus_follows_mouse
end
