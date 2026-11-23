function session.reset
    # Re-apply display and input state after a display switch or at login.
    kde-inhibit --colorCorrect sleep 0.1
    xcalib.reset

    if test "$XDG_SESSION_TYPE" = x11
        xset -r 108
        xset -r 135
    end

    sleep 3
    pkill ibus

    if test "$XDG_SESSION_TYPE" = x11
        xinput set-prop 9 310 1
        xmodmap -e "clear Lock" >/dev/null
        sudo setkeycodes 6e 97 # remap Copilot key to RCtrl
    end

    input.trackball.scroll
end
