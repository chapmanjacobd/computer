function _kscreen_dimmings
    kscreenctl list-outputs --json 2>/dev/null |
        jq -r '.[] | select(.enabled) | [.name, ((.dimming // 1) * 100 | round)] | @tsv'
end
