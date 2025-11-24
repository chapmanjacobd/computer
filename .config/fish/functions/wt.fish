function wt
    if not string match -q -- '* -p*' "$argv"
        kwin.FocusUnderMouse
    end

    /home/xk/.local/bin/lb wt --keep-dir /home/xk/d/library/video/ --action ask_move --exit-code-confirm --ignore-errors --cmd5 'echo skip' --cmd130 exit_multiple_playback --local-media-only --loop ~/lb/video.db $argv

    if not string match -q -- '* -p*' "$argv"
        kwin.FocusFollowsMouse
    end
end
