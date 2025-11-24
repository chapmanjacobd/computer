# Defined interactively
function video.shrink.delete
    ffsmall $argv
    and rm "$argv[1]"
end
