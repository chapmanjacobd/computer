function _screen_brightness_apply --argument-names delta target
    set -l outputs
    if test -n "$target"
        set outputs $target
    else
        set outputs (_plasma_pointer_output)
        if not set -q outputs[1]
            set outputs (kscreen-doctor -j 2>/dev/null | jq -r '.outputs[] | select(.enabled) | .name')
        end
    end

    set -l changes
    for output in $outputs
        set -l current (_kscreen_brightness $output)
        test -n "$current"; or continue
        set -l value (math "min(100, max(1, $current + $delta))")
        set -a changes output.$output.brightness.$value
    end

    if not set -q changes[1]
        echo "brightness: no adjustable outputs found" >&2
        return 1
    end

    kscreen-doctor $changes
end
