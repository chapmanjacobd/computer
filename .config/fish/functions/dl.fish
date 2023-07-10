function dl
    set n (random 1 20)
    echo $n
    eval (sed -n "$n"p /home/xk/.jobs/dl.sh)
end
