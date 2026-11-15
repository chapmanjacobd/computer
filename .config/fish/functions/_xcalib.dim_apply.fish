function _xcalib.dim_apply --argument-names mode
    set -l step 5
    set -q XCALIB_DIM_STEP; and set step $XCALIB_DIM_STEP
    set -l minimum 10
    set -q XCALIB_DIM_MIN; and set minimum $XCALIB_DIM_MIN

    set -l changed 0
    for entry in (_kscreen_dimmings)
        set -l fields (string split -m 1 \t -- $entry)
        set -l output $fields[1]
        set -l current $fields[2]
        set -l value 100
        if test "$mode" = dim
            set value (math "max($minimum, $current - $step)")
        end
        kscreenctl $output set-dimming "$value%"
        or return 1
        set changed 1
    end

    if test $changed -eq 0
        echo "xcalib: no enabled outputs found" >&2
        return 1
    end

    set -l throttle 0.2
    set -q XCALIB_DIM_THROTTLE; and set throttle $XCALIB_DIM_THROTTLE
    sleep $throttle
end
