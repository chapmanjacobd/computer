# Defined interactively
function video.reverse --wraps='ffmpeg'
    ffmpeg -i "$argv" -vf reverse -af areverse (path.withsuffix .reversed "$argv")
end
