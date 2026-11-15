function _xcalib.dim_apply --argument-names mode
    set -l step 5
    set -q XCALIB_DIM_STEP; and set step $XCALIB_DIM_STEP
    set -l minimum 10
    set -q XCALIB_DIM_MIN; and set minimum $XCALIB_DIM_MIN

    set -l changes
    for entry in (_kscreen_dimmings)
        set -l fields (string split -m 1 \t -- $entry)
        set -l output $fields[1]
        set -l current $fields[2]
        set -l value 100
        if test "$mode" = dim
            set value (math "max($minimum, $current - $step)")
        end
        set -a changes output.$output.dimming.$value
    end

    if not set -q changes[1]
        echo "xcalib: no enabled outputs found" >&2
        return 1
    end

    kscreen-doctor $changes
end
