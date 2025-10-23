# Defined interactively
function screenon
    if type wlr-randr
        #WAYLAND_DISPLAY="wayland-0"
        wlr-randr --output HDMI-A-1 --on --auto
    else
        xset dpms force on
    end
end
