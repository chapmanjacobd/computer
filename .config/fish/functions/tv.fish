# Defined interactively
function tv
    set -l hdmi (_kscreen_output 'HDMI(-A)?-[0-9]+')
    if test -z "$hdmi"
        echo "No HDMI output found." >&2
        return 1
    end

    set -l changes output.$hdmi.enable output.$hdmi.mode.1920x1080@60
    for output in (_kscreen_outputs)
        if test "$output" != "$hdmi"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes

    #bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    screen.blank.no && xset s off
    #breaktimer disable && pkill breaktimer

    ~/bin/autostart.sh &
    pkill -9 projectM-pulseau

    sudo pkill -f wheel.py
    run sudo python ~/bin/wheel.py --remap-sides (realpath /dev/input/by-id/usb-Compx_2.4G_Receiver-if01-event-mouse)
    # ultrawideMonocle.off
    windows.maximize.all
    # projectM-pulseaudio &

    system.dpi.125

    set -l sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    while true
        if pactl set-default-sink $sink; and test (pactl get-default-sink) = "$sink"
            break
        end
        sleep 2
    end
    pactl set-sink-volume $sink 45%
end
