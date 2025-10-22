# Defined interactively
function ffmpeg.keyframes
    ffmpeg -nostdin -i "$argv" -c copy -bsf:v 'noise=drop=not(key)' -an -sn -f mpegts - | ffmpeg -f mpegts -i - -vf "setpts=N/FRAME_RATE/TB*8" (path change-extension .keys.mkv "$argv")
end
