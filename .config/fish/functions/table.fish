function table
    set inputs
    set -l x
    while read x
        set inputs $inputs "$x"
    end

    set max 0
    for item in $inputs
        set -l len (echo "$item" | wc -c)
        if test $len -gt $max
            set max $len
        end
    end

    set -l width (math $max + 1)
    set -l display_columns (math "$COLUMNS / $width")
    if test $display_columns -lt 1
        set display_columns 1
    end
    set -l y $display_columns
    for item in $inputs
        if test $y -eq 1
            printf "%s\n" $item
        else
            printf "%-"$width"s" $item
        end

        set y (math "$y - 1")
        if test $y -eq 0
            set y $display_columns
        end
    end

    # print a trailing new line if we haven't yet
    if not test $y -eq $display_columns
        echo
    end
end
