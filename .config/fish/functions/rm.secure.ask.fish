function rm.secure.ask
    if test (count $argv) -eq 0
        echo "Usage: rm.secure.ask <file-or-directory>..." >&2
        return 1
    end

    for target in $argv
        if test -d $target
            set -l nfiles (count (find $target -type f))
            echo "--- $target ($nfiles files) ---"
            find $target -type f -exec ls -lh {} \; | awk '{print $5, $NF}'
        else if test -f $target
            echo "--- $target ---"
            ls -lh $target | awk '{print $5, $NF}'
        else
            echo "rm.secure.ask: $target: not a file or directory" >&2
            continue
        end
        echo

        if confirm "Shred $target?"
            rm.secure $target
        else
            echo "Skipped $target"
        end
    end
end
