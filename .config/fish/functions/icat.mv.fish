# Defined interactively
function icat.mv
    if test (count $argv) -eq 0
        echo "Usage: icat.mv <file1> [file2 ...]"
        return 1
    end

    set -l last_dest ""

    for img in $argv
        if not test -f "$img"
            echo "Skipping '$img': Not a valid file."
            continue
        end

        echo "----------- $img ---"
        kitty +kitten icat "$img"
        echo ""

        set -l choice (pathprompt "icat_mv" "$last_dest")
        if test $status -ne 0
            echo "pathprompt exited with error. Exiting."
            return 1
        end

        if test "$choice" = q -o "$choice" = quit
            echo "Exiting."
            return 0
        else if test -z "$choice"
            if test -n "$last_dest"
                set dest "$last_dest"
            else
                echo "No path specified. Exiting."
                return 1
            end
        else
            set dest "$choice"
        end

        set dest (eval echo $dest)

        mkdir -p "$dest"
        command mv -- "$img" "$dest/"
        set last_dest "$dest"
        echo "Moved $img -> $dest/"
        echo ""
    end
end
