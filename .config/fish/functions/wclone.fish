# Defined interactively
function wclone
    ~/d/53_Scrapbook_Web/
    wget --adjust-extension -e robots=off -np -nc -r -l inf -p --user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" --reject-regex '/tag/|/tags/' $argv
end
