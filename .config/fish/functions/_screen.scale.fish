function _screen.scale --argument-names scale
    # kscreenctl expects a percentage ("125%"), not a scale factor ("1.25").
    set -l value $scale
    if not string match -q '*%' -- $value
        set value (math "round($scale * 100)")%
    end

    for output in (_kscreen_outputs)
        kscreenctl $output set-scale $value
        or return 1
    end
end
