# Defined interactively
function slideshow
    focus_under_mouse

    python -m library.lb view --action ask_move_or_delete --keep-dir /home/xk/d/library/image/ --prefetch 4 --loop --exit-code-confirm -i --cmd130 exit_multiple_playback -m 2 -u time_modified $argv

    focus_follows_mouse
end
