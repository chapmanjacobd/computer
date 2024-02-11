# Defined in /home/xk/.config/fish/functions/ffsmallpar.fish @ line 2
function ffsmallpar
    if not create_lock_file ffsmallpar
        echo "ffsmallpar already running..."
        return 1
    end

    set tmpfile (mktemp)
    fd . $argv -S+200MB | grep -v .small. | sort_size.py >$tmpfile

    if not test -s $tmpfile
        return
    end

    ssh -fN pulse15 # workaround for VisualHostKey
    ssh -fN backup
    cat $tmpfile | timeout -s HUP 18h parallel --sshloginfile ~/.parallel/sshloginfile.ffmpeg --transfer "ffmpeg -nostdin -hide_banner -dn -y -i {} -vf 'scale=-2:min(ih\,1440)' -vcodec libx265 -preset 4 -acodec libopus -b:a 96k {.}.small.mkv && rm {} && rsync -auh --remove-sent-files {.}.small.mkv" $hostname:(pwd) >/dev/null

    for f in (cat $tmpfile)
        if test -e $f -a -e (path change-extension small.mkv $f)
            rm "$f"
            archive (path change-extension small.mkv $f)
        end
    end
    ssh backup fd -HI -eMKV -eMP4 -d1 -x rm
    ssh pulse15 fd -HI -eMKV -eMP4 -d1 -x rm

    clear_lock_file ffsmallpar
end
