# Defined interactively
function wt-dev
    ~/lb/
    python -m xklb.lb watch --keep-dir /mnt/d/70_Now_Watching/Keep/ -u 'ntile(10000) over (order by size / duration) desc' -k delete video.db $argv
end
