#!/usr/bin/awk -f
BEGIN {
    FS = "  # "
}

# For lines with titles, store the title and mark URL as seen
NF == 2 {
    url = $1
    titles[url] = $2
    seen[url] = 1
    # Store the original line to maintain order for titled entries
    if (!(url in original_order)) {
        original_order[url] = NR
        urls_in_order[NR] = url
    }
    next
}

# For lines without titles, just mark URL as seen
NF == 1 {
    url = $1
    seen[url] = 1
    # Store for untitled entries
    if (!(url in original_order)) {
        original_order[url] = NR
        urls_in_order[NR] = url
    }
    next
}

END {
    for (i = 1; i <= NR; i++) {
        if (i in urls_in_order) {
            url = urls_in_order[i]
            if (url in titles) {
                print url "  # " titles[url]
            } else {
                print url
            }
        }
    }
}
