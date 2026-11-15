function xcalib.reset
    if not string match -q 'wayland*' -- "$XDG_SESSION_TYPE"; and not set -q WAYLAND_DISPLAY
        xcalib -clear
        return
    end

    if not command -q kscreen-doctor
        echo "xcalib.reset: kscreen-doctor not found; KDE Wayland is required" >&2
        return 1
    end

    _xcalib.dim_set reset
end
