# Defined interactively
function wtm
    focus_under_mouse
    python -m xklb.lb watch --action ask_move_or_delete --keep-dir /home/xk/d/69_Taxes_Keep/ --prefetch 2 --local -u size desc -S+700M -C --sort-by 'deleted/played desc, deleted desc' --loop --exit-code-confirm -i -m 4 $argv
    focus_follows_mouse
end