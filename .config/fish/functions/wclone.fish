# Defined interactively
function wclone -w wget
    ~/d/dump/text/web/
    wget --force-directories --adjust-extension --page-requisites -e robots=off -np -nc -r -l inf -p --user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" --reject-regex '/tag/|/tags/|\?tag' --tries 8 $argv
    # TODO: https://github.com/rockdaboot/wget2/blob/master/docs/wget2.md#download-options
end
