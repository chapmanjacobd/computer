function _screen.only --argument-names pattern mode rotation
    set -l attempts 15
    set -q SCREEN_ATTEMPTS; and set attempts $SCREEN_ATTEMPTS

    # After a long idle period or a resume, KWin can still be reconnecting the
    # output when this runs. Applying changes to a half-initialized output
    # silently loses them, so retry until the final state is what we asked for.
    set -l seen 0
    for attempt in (seq $attempts)
        set -l target (_kscreen_output $pattern)
        if test -z "$target"
            test $attempt -lt $attempts; and sleep 1
            continue
        end
        set seen 1

        kscreenctl $target set-enabled true
        or return 1

        if test -n "$mode"
            _screen.set_mode $target $mode
            or begin
                test $attempt -lt $attempts; and sleep 1
                continue
            end
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

        # A dimming factor is per-output runtime state in KWin and survives
        # output disable/enable, so clear it whenever an output is switched to.
        if _is_wayland
            kscreenctl $target set-dimming 100% 2>/dev/null
        end

        if _screen.only_verify $target $mode
            return 0
        end

        test $attempt -lt $attempts; and sleep 1
    end

    if test $seen -eq 0
        echo "screen: no output found matching: $pattern" >&2
    else
        echo "screen: could not apply $mode on output matching: $pattern" >&2
    end
    return 1
end
