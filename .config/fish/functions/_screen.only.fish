function _screen.only --argument-names pattern mode rotation
    set -l target (_kscreen_output $pattern)
    if test -z "$target"
        echo "screen: no output found matching: $pattern" >&2
        return 1
    end

    kscreenctl $target set-enabled true
    or return 1

    if test -n "$mode"
        _screen.set_mode $target $mode
        or return 1
    end

    if test -n "$rotation"
        kscreenctl $target set-rotation $rotation
        or return 1
    end

    for output in (_kscreen_outputs)
        test "$output" = "$target"; and continue
        kscreenctl $output set-enabled false
        or return 1
    end
end
