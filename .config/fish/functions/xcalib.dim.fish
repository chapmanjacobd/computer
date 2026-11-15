function xcalib.dim
    if not string match -q 'wayland*' -- "$XDG_SESSION_TYPE"; and not set -q WAYLAND_DISPLAY
        xcalib -red 1 1 99 -green 1 1 95 -blue 1 1 90 -contrast 99 -alter
        return
    end

    if not command -q kscreen-doctor
        echo "xcalib.dim: kscreen-doctor not found; KDE Wayland is required" >&2
        return 1
    end

    _xcalib.dim_set dim
end
