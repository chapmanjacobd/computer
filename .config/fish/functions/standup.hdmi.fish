# Defined interactively
function standup.hdmi
    kscreen-doctor output.DP-1.disable output.HDMI-1.disable output.DVI-D-1.disable
    kscreen-doctor output.HDMI-1.enable output.HDMI-1.rotation.right output.HDMI-1.mode.1920x1080@60
    bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
end
