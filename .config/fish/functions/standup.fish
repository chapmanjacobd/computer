# Defined interactively
function standup
    pkill projectM-jack

    _screen.only 'DVI-D-[0-9]+' 1920x1080@60 270
    or return 1

    # ultrawideMonocle.off
    #bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
    screen blank && xset +dpms
    #breaktimer disable
    pactl set-default-sink alsa_output.usb-Apple__Inc._USB-C_to_3.5mm_Headphone_Jack_Adapter_DWH152405TPJKLTA5-00.analog-stereo
    session.reset &
end
