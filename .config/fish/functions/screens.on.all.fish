# Defined interactively
function screens.on.all
    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.DisplayPort-0.enable output.HDMI-A-0.enable output.DVI-D-0.enable
    else
        kscreen-doctor output.DP-1.enable output.HDMI-1.enable output.DVI-D-1.enable
    end
    bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
end
