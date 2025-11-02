function continue-to
    set substring $argv[1]
    set file (coalesce $argv[2] /dev/stdin)

    cat "$file" | while read line
        if string match -q --ignore-case "*$substring*" "$line"
            break
        end
        echo $line
    end
end
