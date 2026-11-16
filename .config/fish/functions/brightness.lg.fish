function brightness.lg --argument-names action value
    set -l output (kscreenctl list-outputs --names | string match -r '^DP-[0-9]+$' | head -n 1)
    if test -z "$output"
        echo "brightness.lg: no DP output found" >&2
        return 1
    end

    switch $action
        case get
            _kscreen_brightness $output
        case set
            if not set -q value[1]
                echo "usage: brightness.lg set <0-100>" >&2
                return 1
            end
            string match -qr '^[0-9]+$' -- $value; or begin
                echo "usage: brightness.lg set <0-100>" >&2
                return 1
            end
            set -l percent (math "min(100, max(1, $value))")
            _lock brightness "kscreenctl $output set-brightness $percent%"
            or return 1

            set -l cache $XDG_RUNTIME_DIR
            test -d "$cache"; or set cache /tmp
            printf '%s %s\n' (date +%s%N) $percent >$cache/fish-brightness.$output
        case up
            _screen_brightness_adjust +2 $output
        case down
            _screen_brightness_adjust -3 $output
        case '*'
            echo "usage: brightness.lg <get|set <0-100>|up|down>" >&2
            return 1
    end
end
