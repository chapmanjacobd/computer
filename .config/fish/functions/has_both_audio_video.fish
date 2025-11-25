# Defined interactively
function has_both_audio_video
    if ffprobe.has.audio "$argv"; and ffprobe.has.video "$argv"
        return 0
    else
        return 1
    end
end
