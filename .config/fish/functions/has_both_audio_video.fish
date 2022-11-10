# Defined interactively
function has_both_audio_video
    if has_audio "$argv"; and has_video "$argv"
        return 0
    else
        return 1
    end
end
