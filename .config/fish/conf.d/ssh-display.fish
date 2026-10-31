# Give SSH logins the graphical session's display variables, so clipboard
# helpers (cb, xsel, wl-copy) work without hardcoding a display number.
#
# sshd only exports DISPLAY when X11 forwarding is used, but the user systemd
# manager runs inside the graphical session and keeps its environment, so
# `systemctl --user show-environment` reports the live values. Values already
# present (ssh -X, a local shell, a manually set DISPLAY) are left alone.

if set -q SSH_CONNECTION
    for var in DISPLAY WAYLAND_DISPLAY
        set -q $var; and continue
        set -l line (systemctl --user show-environment 2>/dev/null | string match "$var=*" | head -n1)
        set -q line[1]; or continue
        set -l pair (string split -m1 = -- $line[1])
        set -gx $var $pair[2]
    end
end
