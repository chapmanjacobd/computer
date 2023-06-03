# Defined interactively
function previousdiff --argument name
    set name (coalesce $argv[1] 'test')
    set current_output /tmp/cmd_diff_2_$name
    set previous_output /tmp/cmd_diff_1_$name

    cat /dev/stdin | tee $current_output

    if test -e $previous_output
        delta --syntax-theme GitHub --max-line-length 1024 $previous_output $current_output
    end
    mv $current_output $previous_output
end
