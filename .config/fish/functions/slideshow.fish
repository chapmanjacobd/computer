# Defined interactively
function slideshow
    kwin.FocusUnderMouse

    python -m library.lb view --action ask_move_or_delete --keep-dir /home/xk/d/library/image/ --prefetch 4 --loop --exit-code-confirm -i --cmd130 exit_multiple_playback -m 2 -u time_modified $argv

    kwin.FocusFollowsMouse
end
