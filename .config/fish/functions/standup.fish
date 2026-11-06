# Defined interactively
function standup
    pkill projectM-jack

    set -l dvi (_kscreen_output 'DVI-D-[0-9]+')
    if test -z "$dvi"
        echo "No DVI output found." >&2
        return 1
    end
    set -l changes output.$dvi.enable output.$dvi.rotation.right output.$dvi.mode.1920x1080@60
    for output in (_kscreen_outputs)
        if test "$output" != "$dvi"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes
    ultrawideMonocle.off
    #bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    screen.blank && xset +dpms
    #breaktimer disable
    pactl set-default-sink alsa_output.usb-Apple__Inc._USB-C_to_3.5mm_Headphone_Jack_Adapter_DWH152405TPJKLTA5-00.analog-stereo
    ~/bin/autostart.sh &
end
