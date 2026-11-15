function brightness.lg.get
    set -l output (_brightness.lg_output)
    test -n "$output"; or return 1
    _kscreen_brightness $output
end
