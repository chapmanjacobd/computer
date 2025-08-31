# Defined interactively
function cb_append --argument-names suffix
    set temp_file (mktemp -t "cb_append_XXXXXX$suffix")

    while true
        read
        if test $status != 0
            break
        end
        cb >>"$temp_file"
    end
    echo "$temp_file"
end
