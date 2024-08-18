# Defined interactively
function laptop2880
    sudo xrandr --newmode "2880x1726_60.00" 165.25 1920 2040 2240 2560 1038 1041 1051 1077 -hsync +vsync
    sudo xrandr --addmode $argv "2880x1726_60.00"
    xrandr --output $argv --mode "2880x1726_60.00"
end
