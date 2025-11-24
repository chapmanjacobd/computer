# Defined interactively
function urls.submit.wayback
    for url in $argv
        waybackpy -s --archive-url --url $url | grep http
    end
end
