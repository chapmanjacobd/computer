# Defined interactively
function is_corrupt_media
    ffprobe $argv &>/dev/null
    if test $status -ne 0
        echo $argv
    end
end
