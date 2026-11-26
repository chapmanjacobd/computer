function session.reset
    # Re-apply display and input state after a display switch or at login.
    kde-inhibit --colorCorrect sleep 0.1
    xcalib.reset

    if not _is_wayland
        xset -r 108
        xset -r 135
    end

    sleep 3
    pkill ibus

    if not _is_wayland
        xinput set-prop 9 310 1
        xmodmap -e "clear Lock" >/dev/null
        sudo setkeycodes 6e 97 # remap Copilot key to RCtrl
    end

    input.trackball.scroll
end
