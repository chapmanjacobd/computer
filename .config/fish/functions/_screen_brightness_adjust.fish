function _screen_brightness_adjust --argument-names delta target
    set -l command "_screen_brightness_apply $delta"
    test -n "$target"; and set command "$command $target"
    _brightness.lock "$command"
end
