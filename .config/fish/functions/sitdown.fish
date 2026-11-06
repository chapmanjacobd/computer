# Defined interactively
function sitdown
    pkill projectM-jack
    pkill -9 projectM-pulsea

    set -l displayport (_kscreen_output 'DisplayPort-[0-9]+')
    if test -z "$displayport"
        set displayport (_kscreen_output 'DP-[0-9]+')
    end
    if test -z "$displayport"
        echo "No DisplayPort output found." >&2
        return 1
    end

    set -l changes output.$displayport.enable output.$displayport.mode.3440x1440@160
    for output in (_kscreen_outputs)
        if test "$output" != "$displayport"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes

    #bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    ultrawideMonocle.on
    if test "$XDG_SESSION_TYPE" = x11
        kwin_x11 --replace & disown
    else
        qdbus org.kde.KWin /KWin reconfigure
    end

    pactl set-default-sink alsa_output.usb-Apple__Inc._USB-C_to_3.5mm_Headphone_Jack_Adapter_DWH152405TPJKLTA5-00.analog-stereo
    vol 60

    sudo pkill -f wheel.py
    ~/bin/autostart.sh &

    system.dpi.125
end
