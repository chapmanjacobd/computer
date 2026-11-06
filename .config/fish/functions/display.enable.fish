# Defined interactively
function display.enable --argument target
    if not contains -- $target (_kscreen_outputs)
        echo "Unknown output: $target" >&2
        return 1
    end

    set -l changes
    for output in (_kscreen_outputs)
        if test "$output" != "$target"
            set -a changes output.$output.disable
        end
    end
    set -a changes output.$target.enable output.$target.mode.1920x1080@60
    kscreen-doctor $changes
    # ultrawideMonocle.off
    screen.blank.no && xset s off
    pactl set-default-sink alsa_output.pci-0000_01_00.1.hdmi-stereo-extra3
    ~/bin/autostart.sh &
end
