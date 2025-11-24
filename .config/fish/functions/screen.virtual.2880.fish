# Defined interactively
function screen.virtual.2880
    sudo xrandr --newmode "2880x1726_60.00" 423.75 2880 3104 3416 3952 1726 1729 1739 1789 -hsync +vsync
    sudo xrandr --addmode $argv "2880x1726_60.00"
    xrandr --output $argv --mode "2880x1726_60.00"
end
