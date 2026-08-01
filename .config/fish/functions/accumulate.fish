# Defined interactively
function accumulate
    set -l input_file (mktemp)
    set -l selected_file (mktemp)

    cat >$input_file

    while true
        # Extract items from input that are not yet selected
        set -l available (grep -F -x -v -f $selected_file $input_file 2>/dev/null; or cat $input_file)

        if test -z "$available"
            break
        end

        set -l new_selections (string join \n $available | fzf.multi)

        # Break loop if user cancelled or selected nothing
        if test -z "$new_selections"
            break
        end

        echo $new_selections >>$selected_file
    end

    if test -s $selected_file
        cat $selected_file | unique
    end

    rm -f $input_file $selected_file
end
