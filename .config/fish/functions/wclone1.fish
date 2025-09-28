# Defined interactively
function wclone1 -w wget
    ~/d/dump/text/web/
    wget -np -r -l inf --reject-regex '/tag/|/tags/|\?tag' --continue --max-threads=1 --wait=1 --random-wait --https-enforce=none --retry-connrefused $argv
    #--ignore-length
end
