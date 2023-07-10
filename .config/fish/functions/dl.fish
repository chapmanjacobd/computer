function dl
    set n (random 1 (math (filelength /home/xk/.jobs/dl.sh)-1))
    echo $n
    eval (sed -n "$n"p /home/xk/.jobs/dl.sh)
end
