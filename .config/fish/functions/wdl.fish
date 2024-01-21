# Defined interactively
function wdl
    for url in $argv
        rclone copy :http: --http-url "$url" .
    end
end
