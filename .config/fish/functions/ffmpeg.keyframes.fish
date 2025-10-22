# Defined interactively
function ffmpeg.keyframes
    set -l tmpfile (mktemp --suffix .mkv --dry-run)
    mkfifo $tmpfile

    b ffmpeg -nostdin -f mpegts -i $tmpfile -vf "setpts=N/FRAME_RATE/TB*8" (path change-extension .keys.mkv "$argv")
    ffmpeg -nostdin -i "$argv" -c copy -bsf:v 'noise=drop=not(key)' -an -sn -f mpegts pipe:1 >$tmpfile
    wait
    rm $tmpfile
end
