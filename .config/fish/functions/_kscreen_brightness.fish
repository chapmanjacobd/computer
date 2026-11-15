function _kscreen_brightness --argument-names output
    kscreenctl $output --json 2>/dev/null |
        jq -r 'select(.brightness != null) | .brightness * 100 | round'
end
