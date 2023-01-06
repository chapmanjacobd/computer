# Defined interactively
function clip --wraps=ffmpeg --argument file in out
    ffmpeg -i "$file" -ss $in -to $out (fileSuffix "$file" (random_string 5))
end
