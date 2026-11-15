function brightness.lg.down
    set -l output (_brightness.lg_output)
    test -n "$output"; or return 1
    _screen_brightness_adjust -10 $output
end
