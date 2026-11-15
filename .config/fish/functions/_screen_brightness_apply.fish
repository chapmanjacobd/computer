function _screen_brightness_apply --argument-names delta target
    set -l cache $XDG_RUNTIME_DIR
    test -d "$cache"; or set cache /tmp
    set -l now (date +%s%N)
    set -l pointer_file $cache/fish-brightness.pointer

    set -l outputs
    if test -n "$target"
        set outputs $target
    else
        # Resolving the output under the pointer costs several processes. Cache
        # it for the duration of a held key and re-resolve after the TTL.
        set -l cached (_brightness_cache_get $pointer_file $now)
        if test -n "$cached"
            set outputs $cached
        else
            set outputs (_plasma_pointer_output)
            if not set -q outputs[1]
                set outputs (kscreenctl list-outputs --enabled --names)
            end
            if test (count $outputs) -eq 1
                printf '%s %s\n' $now $outputs[1] > $pointer_file
            end
        end
    end

    set -l changed 0
    for output in $outputs
        set -l value_file $cache/fish-brightness.$output
        set -l current (_brightness_cache_get $value_file $now)
        if test -z "$current"
            set current (_kscreen_brightness $output)
        end
        string match -qr '^[0-9]+$' -- "$current"; or continue
        set -l value (math "min(100, max(1, $current + $delta))")
        kscreenctl $output set-brightness "$value%"
        or return 1
        printf '%s %s\n' $now $value > $value_file
        set changed 1
    end

    if test $changed -eq 0
        echo "brightness: no adjustable outputs found" >&2
        return 1
    end

    set -l throttle 0.2
    set -q BRIGHTNESS_THROTTLE; and set throttle $BRIGHTNESS_THROTTLE
    sleep $throttle
end
