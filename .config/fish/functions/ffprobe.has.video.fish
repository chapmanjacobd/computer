# Defined interactively
function ffprobe.has.video --wraps='ffprobe'
    ffprobe -show_streams -select_streams v -loglevel error -i "$argv" | count >/dev/null
end
