# Defined interactively
function wtm
    focus_under_mouse

    python -m library.lb watch --action ask_move_or_delete --keep-dir /home/xk/d/library/porn/video/ --prefetch 2 --loop --exit-code-confirm -i --cmd130 exit_multiple_playback --cmd5 'python -m library.lb process-audio --no-preserve-video' --cmd6 'mv {} /mnt/d/library/porn/vr/' -m 4 $argv

    focus_follows_mouse
end
