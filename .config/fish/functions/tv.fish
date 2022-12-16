# Defined interactively
function tv
    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.HDMI-A-1.disable output.DisplayPort-0.disable output.DVI-D-1.disable
        kscreen-doctor output.HDMI-A-1.enable output.HDMI-A-1.mode.1920x1080@60
    else
        kscreen-doctor output.HDMI-1.disable output.DP-1.disable output.DVI-D-1.disable
        kscreen-doctor output.HDMI-1.enable output.HDMI-1.mode.1920x1080@60
    end
    krohnkite_off
    #bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    keepscreenon && xset s off
    #breaktimer disable && pkill breaktimer
    pactl set-default-sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    ~/.config/autostart.sh &
end
