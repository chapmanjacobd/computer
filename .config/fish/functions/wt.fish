function wt
    ~/lb/
    /home/xk/.local/bin/lb wt video.db -u 'ntile(10000) over (order by size / duration) desc' -k delete $argv
end
