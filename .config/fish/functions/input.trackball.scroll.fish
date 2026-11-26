function input.trackball.scroll
    # Enable hold-to-scroll on trackball buttons. Wayland configures KWin
    # directly and persists it to kcminputrc; X11 uses the libinput driver.
    if _is_wayland
        command -q qdbus; or return 0

        set -l pointers (qdbus org.kde.KWin /org/kde/KWin/InputDevice \
            org.kde.KWin.InputDeviceManager.ListPointers 2>/dev/null)
        for sysname in $pointers
            set -l path /org/kde/KWin/InputDevice/$sysname
            set -l name (qdbus org.kde.KWin $path \
                org.freedesktop.DBus.Properties.Get \
                org.kde.KWin.InputDevice name 2>/dev/null)
            string match -qi '*trackball*' -- "$name"; or continue

            # KWin persists this as ScrollMethod=4. The scroll button keeps
            # its KWin default (BTN_SIDE, 275).
            qdbus org.kde.KWin $path org.freedesktop.DBus.Properties.Set \
                org.kde.KWin.InputDevice scrollOnButtonDown true >/dev/null
        end
        return 0
    end

    set -l device
    for name in (xinput list --name-only 2>/dev/null)
        if string match -qi '*trackball*' -- "$name"
            set device $name
            break
        end
    end
    test -n "$device"; or return 0

    xinput --set-prop $device "libinput Scroll Method Enabled" 0 0 1
    xinput --set-prop $device "libinput Drag Lock Buttons" 9
    xinput --set-prop $device "libinput Button Scrolling Button" 8
    xinput --set-button-map $device 1 8 3 4 5 6 7 2 9
end
