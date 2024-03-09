# Defined interactively
function wtm
    focus_under_mouse
    python -m xklb.lb watch --move-replace --action ask_move_or_delete --keep-dir /home/xk/d/library/porn/video/ --prefetch 2 -u size desc --loop --exit-code-confirm -i --cmd5 'python -m xklb.lb process-audio --split-longer-than 36mins' --cmd6 'mv {} /mnt/d/library/porn/vr/' -m 4 $argv
    focus_follows_mouse
end
