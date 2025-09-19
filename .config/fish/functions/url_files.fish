# Defined interactively
function url_files
    find . -type f -print0 | xargs -0 -n1 awk '
    /^https/ {count++}
    END {
        if (count >= 3) {
            print FILENAME
        }
    }
    '
end
