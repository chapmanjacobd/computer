# Defined interactively
function wclone -w wget
    ~/d/dump/text/web/
    wget --force-directories --adjust-extension --page-requisites -e robots=off -np -r -l inf -p --user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" --reject-regex '/tag/|/tags/|\?tag' --continue --tries=50 --dns-timeout=10 --connect-timeout=5 --read-timeout=45 --http2-request-window=15 --tcp-fastopen $argv
    # --retry-connrefused
    # --ignore-length
    # TODO: https://github.com/rockdaboot/wget2/blob/master/docs/wget2.md#download-options
end
