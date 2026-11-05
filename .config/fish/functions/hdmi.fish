# Defined interactively
function hdmi
    set -l hdmi (_kscreen_output 'HDMI(-A)?-[0-9]+')
    if test -z "$hdmi"
        echo "No HDMI output found." >&2
        return 1
    end

    set -l changes output.$hdmi.enable
    for output in (_kscreen_outputs)
        if test "$output" != "$hdmi"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes
end
