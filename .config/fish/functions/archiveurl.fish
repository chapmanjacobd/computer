# Defined interactively
function archiveurl
    for url in $argv
        waybackpy -s --archive-url --url $url
    end
end
