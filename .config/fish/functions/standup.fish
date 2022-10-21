# Defined interactively
function standup
    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.DisplayPort-0.disable output.HDMI-A-0.disable output.DVI-D-0.disable
        kscreen-doctor output.DVI-D-0.enable output.DVI-D-0.rotation.right output.DVI-D-0.mode.1920x1080@60
    else
        kscreen-doctor output.DP-1.disable output.HDMI-1.disable output.DVI-D-1.disable
        kscreen-doctor output.DVI-D-1.enable output.DVI-D-1.rotation.right output.DVI-D-1.mode.1920x1080@50
    end
    krohnkite_off
    #bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    keepscreenoff && xset +dpms
    #breaktimer disable
    pactl set-default-sink alsa_output.pci-0000_00_1f.3.pro-output-0
    ~/.config/autostart.sh &
end
