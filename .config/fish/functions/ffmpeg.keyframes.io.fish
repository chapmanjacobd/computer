# Defined interactively
function ffmpeg.keyframes.io --argument-names input --argument-names output
    set -l tmpfile (mktemp --suffix .mkv --dry-run)
    mkfifo $tmpfile

    b ffmpeg -nostdin -f mpegts -i $tmpfile -vf "setpts=N/FRAME_RATE/TB*8" "$output"
    ffmpeg -nostdin -i "$input" -c copy -bsf:v 'noise=drop=not(key)' -an -sn -f mpegts pipe:1 >$tmpfile
    wait
    rm $tmpfile
end
