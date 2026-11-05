# Defined interactively
function screens.on.all
    set -l changes
    for output in (_kscreen_outputs)
        set -a changes output.$output.enable
    end
    kscreen-doctor $changes
    bash -c 'kquitapp6 plasmashell || killall plasmashell; systemd-run --user kstart plasmashell'
end
