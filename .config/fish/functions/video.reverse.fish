# Defined interactively
function video.reverse
    ffmpeg -i "$argv" -vf reverse -af areverse (path change-extension '' "$argv").reversed.(path extension "$argv")
end
