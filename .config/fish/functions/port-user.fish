function port-user
    set -l pid (sudo lsof -t -i:$argv[1])
    if count $pid >/dev/null
        for id in $pid
        set -l cmd (ps -p $id -o command | tail -n 1)
        printf "PID: %s\n" $id
        printf "CMD: %s\n" $cmd
        end
    else
        echo nope
    end
end
