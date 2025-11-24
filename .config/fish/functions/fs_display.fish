# Defined interactively
function fs_display --argument target
    for enabled in (kscreen-doctor -o | grep -v disconnected | grep -i enabled | cut -d' ' -f3)
        kscreen-doctor output.$enabled.disable
    end
    kscreen-doctor output.$target.enable output.$target.mode.1920x1080@60
    krohnkite.off
    keepscreenon && xset s off
    pactl set-default-sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    ~/bin/autostart.sh &
end
