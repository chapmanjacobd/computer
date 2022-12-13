# Defined interactively
function sitdown
    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.HDMI-A-0.disable output.DisplayPort-0.disable output.DVI-D-0.disable
        kscreen-doctor output.DisplayPort-0.enable
    end
    if grep -qEi "(DP-1)" (kscreen-doctor -o | psub)
        kscreen-doctor output.HDMI-1.disable output.DP-1.disable output.DVI-D-0.disable
        kscreen-doctor output.DP-1.enable
    end
    krohnkite_on
    bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    kwin_x11 --replace & disown
    pactl set-default-sink alsa_output.pci-0000_00_1f.3.pro-output-0
    ~/.config/autostart.sh &
end
