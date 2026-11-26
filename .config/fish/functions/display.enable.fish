# Defined interactively
function display.enable --argument target
    _screen.only $target 1920x1080@60
    or return 1
    # ultrawideMonocle.off
    screen blank no
    not _is_wayland; and xset s off
    pactl set-default-sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    session.reset &
end
