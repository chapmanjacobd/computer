function rm.secure.ask
    if test (count $argv) -eq 0
        echo "Usage: rm.secure.ask <directory>..." >&2
        return 1
    end

    for target in $argv
        if not test -d $target
            echo "rm.secure.ask: $target: not a directory" >&2
            continue
        end

        echo "--- $target ---"
        find $target -type f -exec ls -lh {} \; | awk '{print $5, $NF}'
        echo
        echo (count (find $target -type f)) files
        echo

        if confirm.yes "Shred $target?"
            rm.secure $target
        else
            echo "Skipped $target"
        end
    end
end
