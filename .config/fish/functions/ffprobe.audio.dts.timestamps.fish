# Defined interactively
function ffprobe.audio.dts.timestamps
    ffprobe -v error -of default=noprint_wrappers=1:nokey=1 -select_streams a:0 -show_frames -show_entries frame=pkt_dts_time $argv
end
