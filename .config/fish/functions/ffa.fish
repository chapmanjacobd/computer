# Defined interactively
function ffa
    ffmpeg -i "$argv" -vn -y -c:a copy (path change-extension mka "$argv")
end
