# Defined interactively
function ffmpeg.decode.report --wraps='ffmpeg'
    ffmpeg -nostdin -nostats -report -i $argv -f null /dev/null
end
