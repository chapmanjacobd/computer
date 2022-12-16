# Defined in - @ line 1
function scr
    scrot output.png
    convert output.png \( -clone 0 -crop 48x48+700+560 -repage 240x48+0+0 \) \( -clone 0 -crop 48x48+850+420 -repage 240x48+48+0 \) \( -clone 0 -crop 48x48+950+550 -repage 240x48+96+0 \) \( -clone 0 -crop 48x48+1200+400 -repage 240x48+144+0 \) \( -clone 0 -crop 48x48+1200+800 -repage 240x48+192+0 \) -flatten -crop 240x48+0+0 output.png
end
