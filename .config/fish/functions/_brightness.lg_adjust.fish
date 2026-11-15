function _brightness.lg_adjust --argument-names delta
    set -l current (brightness.lg.get)
    if test -z "$current"
        echo "brightness.lg: could not read current brightness" >&2
        return 1
    end

    _brightness.lg_write (math "$current + $delta")
    pkill -f brightness_lg
end
