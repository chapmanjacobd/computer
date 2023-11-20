# Defined interactively
function wtm
    focus_under_mouse
    python -m xklb.lb watch --move-replace --action ask_move_or_delete --keep-dir /home/xk/d/69_Taxes_Keep/ --prefetch 2 --local -u size desc -C --sort-by 'deleted/played desc, deleted desc' --loop --exit-code-confirm -i --cmd5 ~/bin/process_audio.py --cmd6 'mv {} /mnt/d/68_Vr_Tv/' -m 4 $argv
    focus_follows_mouse
end
