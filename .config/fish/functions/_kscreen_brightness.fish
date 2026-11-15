function _kscreen_brightness --argument-names output
    kscreen-doctor -j 2>/dev/null |
        jq -r --arg output "$output" '.outputs[] | select(.name == $output) | .brightness * 100 | round'
end
