# Defined interactively
function wclone -w wget
    ~/d/dump/text/web/
    wget --force-directories -np -r -l inf --reject-regex '/tag/|/tags/|\?tag' --continue $argv
    # --max-threads=1 --wait=1 --random-wait --https-enforce=none
    # --retry-connrefused
    # --ignore-length
end
