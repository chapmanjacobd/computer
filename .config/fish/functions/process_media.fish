# Defined interactively
function process_media
    for s in (fd -td -d2 processing /mnt/) (fd -td -d1 processing /home/xk/)
        tmux-append lb shrink -vy $s
    end
end
