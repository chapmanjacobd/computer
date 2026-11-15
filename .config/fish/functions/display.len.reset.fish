# Defined interactively
function display.len.reset
    set -l edp (_kscreen_output 'eDP-[0-9]+')
    test -n "$edp"; or return 1
    kscreenctl $edp set-enabled true; or return 1
    _screen.set_mode $edp 2880x1800@60
    brightness.down
end
