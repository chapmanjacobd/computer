# Defined interactively
function screenoff
    if type -q wlr-randr
        # WAYLAND_DISPLAY="wayland-0"
        wlr-randr --output HDMI-A-1 --off
    else
        xset dpms force off
    end
end
