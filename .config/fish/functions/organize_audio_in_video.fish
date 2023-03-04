# Defined interactively
function organize_audio_in_video
    has_video "$argv"
    set video $status

    has_audio "$argv"
    set audio $status

    if test $video -eq 0 -a $audio -eq 0
        return 0
    else if test $video -eq 0
        mv "$argv" ~/d/61_Photos_Unsorted/gifs/from_video/
        return 0
    else if test $audio -eq 0
        mv "$argv" ~/d/82_Audiobooks/unsorted/from_video/
    end
end
