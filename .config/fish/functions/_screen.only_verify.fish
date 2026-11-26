function _screen.only_verify --argument-names target mode
    set -l state (kscreenctl $target --json 2>/dev/null |
        jq -r '[.enabled, .mode.resolution.width, .mode.resolution.height] | @tsv' 2>/dev/null)
    test -n "$state"; or return 1

    set -l fields (string split \t -- $state)
    test "$fields[1]" = true; or return 1

    if test -n "$mode"
        set -l resolution (string replace -r '@.*' '' -- $mode)
        set -l size (string split x -- $resolution)
        test "$fields[2]" = "$size[1]"; or return 1
        test "$fields[3]" = "$size[2]"; or return 1
    end

    # Only the requested output should remain enabled.
    set -l enabled (kscreenctl list-outputs --enabled --names)
    test (count $enabled) -eq 1; and test "$enabled[1]" = "$target"
end
