# Defined interactively
function wclone -w wget
    ~/d/dump/text/web/
    wget -np -r -l inf --reject-regex '/tag/|/tags/|\?tag' --continue $argv
    # --retry-connrefused
    # --ignore-length
    # TODO: https://github.com/rockdaboot/wget2/blob/master/docs/wget2.md#download-options
end
