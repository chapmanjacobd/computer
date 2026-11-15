function _xcalib.apply --argument-names mode
    if not string match -q 'wayland*' -- "$XDG_SESSION_TYPE"; and not set -q WAYLAND_DISPLAY
        if test "$mode" = dim
            xcalib -red 1 1 99 -green 1 1 95 -blue 1 1 90 -contrast 99 -alter
        else
            xcalib -clear
        end
        return
    end

    if not command -q kscreenctl
        echo "xcalib: kscreenctl not found; KDE Wayland is required" >&2
        return 1
    end

    _lock xcalib.dimming "_xcalib.dim_apply $mode"
end
