# Defined interactively
function stdin_or_file
    set file (coalesce $argv[1] /dev/stdin)

    cat "$file" | while read line
        echo $line
    end
end
