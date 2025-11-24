# Defined interactively
function tv
    if grep -qEi "(DisplayPort-0)" (kscreen-doctor -o | psub)
        kscreen-doctor output.HDMI-A-0.enable output.HDMI-A-0.mode.1920x1080@60
        kscreen-doctor output.DisplayPort-0.disable output.DVI-D-0.disable
    else
        kscreen-doctor output.HDMI-1.enable output.HDMI-1.mode.1920x1080@60
        kscreen-doctor output.DP-1.disable output.DVI-D-0.disable
    end
    #bash -c 'kquitapp5 plasmashell || killall plasmashell; kstart5 plasmashell'
    keepscreenon && xset s off
    #breaktimer disable && pkill breaktimer
    pactl set-default-sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    vol 65
    ~/bin/autostart.sh &
    pkill -9 projectM-pulseau

    sudo pkill -f wheel.py
    run sudo python ~/bin/wheel.py --remap-sides (realpath /dev/input/by-id/usb-Compx_2.4G_Receiver-if01-event-mouse)
    krohnkite.off
    windows.maximize.all
    # projectM-pulseaudio &
end
