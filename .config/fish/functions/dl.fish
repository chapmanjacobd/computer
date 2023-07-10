function dl
    set n (random 1 (filelength /home/xk/.jobs/dl.sh))
    echo $n
    eval (sed -n "$n"p /home/xk/.jobs/dl.sh)
end
