# Defined via `source`
function redirects
    if test (count $argv) -eq 0
        echo "Usage: redirects <url>"
        return 1
    end

    set url $argv[1]

    while true
        # Fetch headers only
        set headers (curl -s -I $url)

        # Extract status code
        set http_status (echo $headers | grep -oE "HTTP/[0-9.]+ [0-9]+" | tail -n1 | awk '{print $2}')

        echo "$htp_status -> $url"

        # Extract redirect location
        set location (echo $headers | grep -i "^Location:" | sed 's/Location: //I' | tr -d '\r')

        if test -z "$location"
            break
        end

        set url $location
    end
end
