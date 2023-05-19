# Defined interactively
function ffsmallpar
    set tmpfile (mktemp)
    fd -S+200MB | grep -v .small. >$tmpfile
    cat $tmpfile | parallel --dry-run --sshlogin :,backup,pulse15 --jobs 3,2,2 --transfer --return {.}.small.mkv --cleanup ffmpeg -nostdin -hide_banner -dn -y -i {} -vf "scale=-2:min(ih\,1440)" -vcodec libx265 -preset 4 -acodec libopus -b:a 96k {.}.small.mkv
    cat $tmpfile | parallel --dry-run rm
end
