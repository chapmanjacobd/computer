# Defined interactively
function screen.virtual.laptop
    sudo xrandr --newmode "1920x1038_60.00" 165.25 1920 2040 2240 2560 1038 1041 1051 1077 -hsync +vsync
    sudo xrandr --addmode $argv "1920x1038_60.00"
    xrandr --output $argv --mode "1920x1038_60.00"
end
