# Defined interactively
function wget.single
    wget --force-directories --adjust-extension --page-requisites -e robots=off --span-hosts --convert-links --user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" --reject-regex '/tag/|/tags/|\?tag' --tries=3 --dns-timeout=10 --connect-timeout=5 --read-timeout=45 --http2-request-window=15 --tcp-fastopen $argv
end
