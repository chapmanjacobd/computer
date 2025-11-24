# Defined interactively
function stdin.or.file
    set file (coalesce $argv[1] /dev/stdin)

    cat "$file" | while read line
        echo $line
    end
end
