# Defined interactively
function screenon
    if type -q wlr-randr
        #WAYLAND_DISPLAY="wayland-0"
        wlr-randr --output HDMI-A-1 --on
    else
        xset dpms force on
    end
end
