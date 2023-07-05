# Defined interactively
function tv
    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.HDMI-A-0.enable output.HDMI-A-0.mode.1920x1080@60
        kscreen-doctor output.DisplayPort-0.disable output.DVI-D-0.disable
    else
        kscreen-doctor output.HDMI-1.enable output.HDMI-1.mode.1920x1080@60
        kscreen-doctor output.DP-1.disable output.DVI-D-0.disable
    end
    krohnkite_off
    #bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    keepscreenon && xset s off
    #breaktimer disable && pkill breaktimer
    pactl set-default-sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    ~/.config/autostart.sh &
    pkill -9 projectM-pulseau
    projectM-pulseaudio &
end
