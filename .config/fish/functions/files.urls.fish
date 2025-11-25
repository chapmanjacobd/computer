# Defined interactively
function files.urls
    find . -type f -print0 | xargs -0 -n1 awk '
    /^https/ {
        url_count++
    }
    !/^https/ {
        non_url_count++
    }
    END {
        if (url_count >= 3 && non_url_count <= 2) {
            print FILENAME
        }
    }
    '
end
