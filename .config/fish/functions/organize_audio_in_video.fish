# Defined interactively
function organize_audio_in_video -a db
    wt --db $db -w 'video_count=0 and audio_count>=1' -pf | parallel mv {} ~/d/dump/audio/audiobooks/unsorted/from_video/
    wt --db $db -w 'video_count>=1 and audio_count=0' -pf | parallel mv {} ~/d/dump/porn/image/gifs/from_video/
end
