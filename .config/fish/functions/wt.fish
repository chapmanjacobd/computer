function wt
    ~/lb/
    /home/xk/.local/bin/lb wt video.db -k delete -u 'ntile(10000) over (order by size / duration) desc' $argv
end
