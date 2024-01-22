# Defined interactively
function wdl
    for url in $argv
        set parent (string unescape --style=url (path basename $url))
        mkdir $parent/
        ./$parent/
        rclone copy :http: --http-url "$url" .
        ..
    end
end
