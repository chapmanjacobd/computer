# Defined interactively
function cb_append_html
    set temp_file (mktemp -t 'cb_append_XXXXXX.html')

    while true
        read
        if test $status != 0
            break
        end
        cb -t text/html >>"$temp_file"
    end
    echo "$temp_file"
end
