function _xcalib.dim_apply --argument-names mode
    set -l step 5
    set -q XCALIB_DIM_STEP; and set step $XCALIB_DIM_STEP
    set -l minimum 10
    set -q XCALIB_DIM_MIN; and set minimum $XCALIB_DIM_MIN

    # Resetting must cover disabled outputs as well: KWin keeps each output's
    # dimming value and restores it when the output is enabled again, so a dim
    # left behind on the TV reappears after switching to it.
    set -l outputs
    set -l values
    if test "$mode" = dim
        for entry in (_kscreen_dimmings)
            set -l fields (string split -m 1 \t -- $entry)
            set -a outputs $fields[1]
            set -a values (math "max($minimum, $fields[2] - $step)")
        end
    else
        set outputs (_kscreen_outputs)
        for output in $outputs
            set -a values 100
        end
    end

    set -l changed 0
    for i in (seq (count $outputs))
        kscreenctl $outputs[$i] set-dimming "$values[$i]%"
        or return 1
        set changed 1
    end

    if test $changed -eq 0
        echo "xcalib: no outputs found" >&2
        return 1
    end

    set -l throttle 0.2
    set -q XCALIB_DIM_THROTTLE; and set throttle $XCALIB_DIM_THROTTLE
    sleep $throttle
end
