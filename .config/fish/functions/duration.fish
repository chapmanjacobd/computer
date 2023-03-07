# Defined interactively
function duration
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $argv
end
