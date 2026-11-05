# Defined interactively
function standup.hdmi
    set -l hdmi (_kscreen_output 'HDMI(-A)?-[0-9]+')
    if test -z "$hdmi"
        echo "No HDMI output found." >&2
        return 1
    end

    set -l changes output.$hdmi.enable output.$hdmi.rotation.right output.$hdmi.mode.1920x1080@60
    for output in (_kscreen_outputs)
        if test "$output" != "$hdmi"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes
    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
end
