# Defined via `source`
function cb_append_html
    set temp_file (mktemp -t 'cb_append_XXXXXX.html')
    echo "$temp_file" >&2

    while true
        cb | head -n 1 >&2
        cb | tail -n 1 >&2
        cb -t text/html >>"$temp_file"
        echo "" >>"$temp_file"

        echo '' >&2  # This prevents the shell's default 'read>' prompt from overwriting our output in stderr
        read __dummy__
        if test $status != 0
            break
        end
    end
    echo "$temp_file"
end
