function brightness.lg.up
    set -l output (_brightness.lg_output)
    test -n "$output"; or return 1
    _screen_brightness_adjust +5 $output
end
