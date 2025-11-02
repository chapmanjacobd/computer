function continue-from
    set substring $argv[1]
    set file (coalesce $argv[2] /dev/stdin)

    set found_match false
    cat "$file" | while read line
        if $found_match; or string match -q --ignore-case "*$substring*" "$line"
            set found_match true
            echo $line
        end
    end
end
