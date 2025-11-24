# Defined interactively
function tv.dvi
    kscreen-doctor output.HDMI-A-0.disable output.DisplayPort-1.disable output.DVI-D-0.disable
    kscreen-doctor output.DVI-D-0.enable output.DVI-D-0.mode.1920x1080@60
    bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
end
