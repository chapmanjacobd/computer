function _screen.scale --argument-names scale
    for output in (_kscreen_outputs)
        kscreenctl $output set-scale $scale
        or return 1
    end
end
