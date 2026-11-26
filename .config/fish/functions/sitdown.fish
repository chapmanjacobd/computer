# Defined interactively
function sitdown
    pkill projectM-jack
    pkill -9 projectM-pulsea

    _screen.only 'DisplayPort-[0-9]+|DP-[0-9]+' 3440x1440@160
    or return 1
    screen blank 300
    # ultrawideMonocle.on

    pactl set-default-sink alsa_output.usb-Apple__Inc._USB-C_to_3.5mm_Headphone_Jack_Adapter_DWH152405TPJKLTA5-00.analog-stereo
    vol 60

    sudo pkill -f wheel.py
    session.reset &

    system.dpi.125
end
