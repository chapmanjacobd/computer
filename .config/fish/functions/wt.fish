function wt
    if not string match -q -- '*-p*' "$argv"
        focus_under_mouse
    end

    /home/xk/.local/bin/lb wt --keep-dir /home/xk/d/library/video/ --action ask_move_or_delete --exit-code-confirm --cmd5 'echo skip' --cmd130 exit_multiple_playback --local-media-only ~/lb/video.db $argv

    if not string match -q -- '*-p*' "$argv"
        focus_follows_mouse
    end
end
