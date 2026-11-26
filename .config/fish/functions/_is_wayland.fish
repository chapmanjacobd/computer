function _is_wayland
    test -n "$WAYLAND_DISPLAY"; or test "$XDG_SESSION_TYPE" = wayland
end
