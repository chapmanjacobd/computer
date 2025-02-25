function wt
    if not string match -q -- '*-p*' "$argv"
        focus_under_mouse
    end

    /home/xk/.local/bin/lb wt --keep-dir /mnt/d/archive/video/other/ -k delete --local-media-only ~/lb/video.db --cmd5 'echo skip' $argv

    if not string match -q -- '*-p*' "$argv"
        focus_follows_mouse
    end
end
