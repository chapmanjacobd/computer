# Defined interactively
function ffclip --wraps=ffmpeg --argument file in out
    ffmpeg -i "$file" -ss $in -to $out (path.withsuffix "$file" (chars.random 5))
end
