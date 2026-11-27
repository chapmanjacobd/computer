# Defined interactively
function ffprobe.json --wraps='ffprobe'
    ffprobe -show_format -show_streams -of json $argv
end
