# Defined interactively
function video.shrink.delete
    video.shrink $argv
    and rm "$argv[1]"
end
