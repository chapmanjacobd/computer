# Defined interactively
function has_video
    ffprobe -show_streams -select_streams v -loglevel error -i "$argv" | count >/dev/null
end
