# Defined interactively
function has_audio
    ffprobe -show_streams -select_streams a -loglevel error -i "$argv" | count >/dev/null
end
