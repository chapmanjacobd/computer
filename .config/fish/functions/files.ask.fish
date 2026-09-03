function files.ask
    if test (count $argv) -eq 0
        echo "Usage: files.ask <directory>..." >&2
        return 1
    end

    set -l result

    for target in $argv
        if not test -d $target
            echo "files.ask: $target: not a directory" >&2
            continue
        end

        set -l list (find $target -type f)
        set -l nfiles (count $list)

        echo "--- $target ($nfiles files) ---"
        for f in $list
            ls -lh $f | awk '{print $5, $NF}'
        end
        echo

        if confirm "Expand $target?"
            set -a result $list
        else
            echo "Skipped $target"
        end
    end

    for f in $result
        echo $f
    end
end
