# Defined interactively
function ffsmallpar
    if pgrep parallel
        echo "Parallel already running..."
        return 1
    end

    set tmpfile (mktemp)
    fd -S+200MB | grep -v .small. >$tmpfile

    if not test -s $tmpfile
        return
    end

    ssh -fN pulse15 # workaround for VisualHostKey
    ssh -fN backup
    cat $tmpfile | parallel --filter-hosts --sshlogin backup,pulse15,: --jobs 2,2,3 --transfer "ffmpeg -nostdin -hide_banner -dn -y -i {} -vf 'scale=-2:min(ih\,1440)' -vcodec libx265 -preset 4 -acodec libopus -b:a 96k {.}.small.mkv && rm {} && rsync -auh --remove-sent-files {.}.small.mkv" $hostname:(pwd)
    and cat $tmpfile | parallel rm || true
    or cat $tmpfile >~/ffsmallpar_errors.txt
end
