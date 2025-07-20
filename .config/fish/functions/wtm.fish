# Defined interactively
function wtm
    if not string match -q -- '*-p*' "$argv"
        focus_under_mouse
    end

    python -m library.lb watch --prefetch 2 --loop --cmd130 exit_multiple_playback --cmd5 'python -m library.lb process-audio --no-preserve-video' -m 4 --fstack $argv

    if not string match -q -- '*-p*' "$argv"
        focus_follows_mouse
    end
end
