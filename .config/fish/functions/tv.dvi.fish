# Defined interactively
function tv.dvi
    set -l dvi (_kscreen_output 'DVI-D-[0-9]+')
    if test -z "$dvi"
        echo "No DVI output found." >&2
        return 1
    end

    set -l changes output.$dvi.enable output.$dvi.mode.1920x1080@60
    for output in (_kscreen_outputs)
        if test "$output" != "$dvi"
            set -a changes output.$output.disable
        end
    end
    kscreen-doctor $changes
    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
end
