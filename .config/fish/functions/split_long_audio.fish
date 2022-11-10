# Defined interactively
function split_long_audio --argument f
    if test (duration "$f") -gt 2280
        echo $f
        split_by_silence "$f"
    end
end
