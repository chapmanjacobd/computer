# Defined interactively
function wtseek
    kwin.FocusUnderMouse
    b repeatdelay 0.7 xdotool key i
    set key_pid (jobs -lp)

    wt $argv

    kill $key_pid
    kwin.FocusFollowsMouse
end
