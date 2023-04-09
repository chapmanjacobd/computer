function wt
    /home/xk/.local/bin/lb wt --keep-dir /mnt/d/70_Now_Watching/Keep/ -u 'ntile(10000) over (order by size / duration) desc' -k delete ~/lb/video.db $argv
end
