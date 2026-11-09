# Defined interactively
function http.size
    if test (count $argv) -eq 0
        echo "Usage: http.size <URL>"
        return 1
    end

    set -l target $argv[1]

    echo "Fetching sizes for: $target"

    echo -n "Uncompressed: "
    curl -so /dev/null "$target" -w "%{size_download} bytes\n"

    echo -n "Gzipped:      "
    curl -H "Accept-Encoding: gzip" -so /dev/null "$target" -w "%{size_download} bytes\n"
end
