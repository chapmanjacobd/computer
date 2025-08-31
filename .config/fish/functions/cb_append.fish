# Defined via `source`
function cb_append --argument-names suffix
    set temp_file (mktemp -t "cb_append_XXXXXX$suffix")
    echo "$temp_file" >&2

    while true
        text_preview (cbfile) >&2

        cb >>"$temp_file"
        echo '' >>"$temp_file"

        echo '' >&2  # This prevents the shell's default 'read>' prompt from overwriting our output in stderr
        read __dummy__
        if test $status != 0
            break
        end
    end
    echo "$temp_file"
end
