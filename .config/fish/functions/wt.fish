function wt
    ~/lb/
    /home/xk/.local/bin/lb wt -k delete -u 'ntile(10000) over (order by size / duration) desc' $argv
end
