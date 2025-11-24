# Defined interactively
function standup
    pkill projectM-jack

    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.DVI-D-0.enable output.DVI-D-0.rotation.right output.DVI-D-0.mode.1920x1080@60
        kscreen-doctor output.DisplayPort-0.disable output.HDMI-A-0.disable
    else
        kscreen-doctor output.DVI-D-0.enable output.DVI-D-0.rotation.right output.DVI-D-0.mode.1920x1080@50
        kscreen-doctor output.DP-1.disable output.HDMI-1.disable
    end
    krohnkite.off
    #bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    screen.blank && xset +dpms
    #breaktimer disable
    pactl set-default-sink alsa_output.usb-Apple__Inc._USB-C_to_3.5mm_Headphone_Jack_Adapter_DWH152405TPJKLTA5-00.analog-stereo
    ~/bin/autostart.sh &
end
