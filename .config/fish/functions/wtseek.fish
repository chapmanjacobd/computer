# Defined interactively
function wtseek
    focus_under_mouse
    b repeatdelay 1.1 xdotool key o
    set key_pid (jobs -lp)

    wt $argv

    kill $key_pid
    focus_follows_mouse
end
