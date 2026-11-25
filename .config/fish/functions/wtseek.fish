# Defined interactively
function wtseek
    kwin.FocusUnderMouse
    b repeat.delay 0.7 _dotool_key i
    set key_pid (jobs -lp)

    wt $argv

    kill $key_pid
    kwin.FocusFollowsMouse
end
