function trackpad.on.with.keyboard
    if test "$XDG_SESSION_TYPE" = wayland; and command -q qdbus
        set -l pointers (qdbus org.kde.KWin /org/kde/KWin/InputDevice \
            org.kde.KWin.InputDeviceManager.ListPointers 2>/dev/null)
        for sysname in $pointers
            set -l path /org/kde/KWin/InputDevice/$sysname
            set -l name (qdbus org.kde.KWin $path \
                org.freedesktop.DBus.Properties.Get \
                org.kde.KWin.InputDevice name 2>/dev/null)
            string match -qi '*touchpad*' -- "$name"; or string match -qi '*trackpad*' -- "$name"; or continue
            set -l supported (qdbus org.kde.KWin $path \
                org.freedesktop.DBus.Properties.Get \
                org.kde.KWin.InputDevice supportsDisableWhileTyping 2>/dev/null)
            test "$supported" = true; or continue
            qdbus org.kde.KWin $path org.freedesktop.DBus.Properties.Set \
                org.kde.KWin.InputDevice disableWhileTyping false >/dev/null 2>&1
        end
        return 0
    end

    xinput --set-prop 11 329 0
end
