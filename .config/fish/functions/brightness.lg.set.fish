function brightness.lg.set
    if not set -q argv[1]
        echo "usage: brightness.lg.set <0-100>" >&2
        return 1
    end

    set -l output (_brightness.lg_output)
    test -n "$output"; or return 1
    set -l value (math "min(100, max(1, $argv[1]))")
    _brightness.lock "kscreen-doctor output.$output.brightness.$value"
end
