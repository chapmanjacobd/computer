# Defined interactively
function stdin_count_failed
    set count_failed 0
    set count_success 0

    while read -l file
        $argv $file
        if test $status -eq 0
            set count_success (math $count_success + 1)
        else
            set count_failed (math $count_failed + 1)
        end

    end

    echo "Succeeded: $count_success"
    echo "Failed: $count_failed"
end
