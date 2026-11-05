function _kscreen_output --argument-names pattern
    _kscreen_outputs | string match -r "^$pattern\$" | head -n 1
end
