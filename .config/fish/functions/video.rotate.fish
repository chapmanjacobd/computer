# Defined interactively
function video.rotate
    set deg (coalesce $argv[2] -90)
    ffmpeg -i $argv[1] -metadata:s:v rotate="$deg" -codec copy (path change-extension '' $argv[1]).rotated.(path extension $argv[1])
end
