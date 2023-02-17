function wt
    /home/xk/.local/bin/lb wt -u 'ntile(10000) over (order by size / duration) desc' -k delete ~/lb/video.db $argv
end
