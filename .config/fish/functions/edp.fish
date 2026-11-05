# Defined interactively
function edp
    set -l edp (_kscreen_output 'eDP-[0-9]+')
    if test -z "$edp"
        echo "No eDP output found." >&2
        return 1
    end

    set -l changes output.$edp.enable
    for output in (_kscreen_outputs)
        if test "$output" != "$edp"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes
end
