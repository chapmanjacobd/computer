# Defined interactively
function wtm
    focus_under_mouse
    b repeatdelay 1.1 xdotool key o
    set key_pid (jobs -lp)

    python -m xklb.lb watch --replace --action ask_move_or_delete --keep-dir /home/xk/d/library/porn/video/ --prefetch 2 -u size desc --loop --exit-code-confirm -i --cmd130 exit_multiple_playback --cmd5 'python -m xklb.lb process-audio --audio-only' --cmd6 'mv {} /mnt/d/library/porn/vr/' -m 4 $argv

    kill $key_pid
    focus_follows_mouse
end
