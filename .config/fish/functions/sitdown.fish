# Defined interactively
function sitdown
    pkill projectM-jack
    pkill -9 projectM-pulsea

    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.DisplayPort-0.enable output.DisplayPort-0.mode.3440x1440@160
        kscreen-doctor output.HDMI-A-0.disable output.DVI-D-0.disable
    end
    if grep -qEi "(DP-1)" (kscreen-doctor -o | psub)
        kscreen-doctor output.DP-1.enable output.DP-1.mode.3440x1440@160
        kscreen-doctor output.HDMI-1.disable output.DVI-D-0.disable
    end
    #bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    kwriteconfig5 --file kwinrc --group Script-krohnkite enableTileLayout false
    krohnkite.on
    kwin_x11 --replace & disown
    pactl set-default-sink alsa_output.usb-Apple__Inc._USB-C_to_3.5mm_Headphone_Jack_Adapter_DWH152405TPJKLTA5-00.analog-stereo
    vol 40
    sudo pkill -f wheel.py
    ~/bin/autostart.sh &
end
