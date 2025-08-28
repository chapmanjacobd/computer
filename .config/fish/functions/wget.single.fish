# Defined interactively
function wget.single
    for url in $argv
        timeout 5m wget2 --user-agent="$(useragent)" --span-hosts -v "$url"
    end
end
