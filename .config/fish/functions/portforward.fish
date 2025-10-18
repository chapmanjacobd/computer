# Defined interactively
function portforward
    if test (count $argv) -ne 2
        echo "Usage: portforward <computer_name> <remote_port>" >&2
        return 1
    end

    set -l computer_name $argv[1]
    set -l remote_port $argv[2]
    set -l local_port (freeport $remote_port)
    if test $status -ne 0
        echo "Error: Failed to find a free local port starting from $remote_port." >&2
        return 1
    end

    ssh -N -L 127.0.0.1:$local_port:127.0.0.1:$remote_port $computer_name
    set -l pid $last_pid

    echo http://127.0.0.1:$local_port
    commandline -r "kill $pid"
end
