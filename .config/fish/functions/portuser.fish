function portuser
    set -l pid (sudo lsof -t -i:$argv[1])
    if count $pid >/dev/null
        for id in $pid
            set -l cmd (ps -p $id -o command | tail -n 1)
            printf "%s\t%s\n" $id $cmd
        end
    else
        echo nope
    end
end
