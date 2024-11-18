# Defined interactively
function ffmpeg.frames
    ffprobe -v fatal -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=noprint_wrappers=1:nokey=1 $argv
end
