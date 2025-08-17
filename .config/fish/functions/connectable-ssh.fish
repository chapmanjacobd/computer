# Defined interactively
function connectable-ssh
    for host in $argv
        ssh -o ConnectTimeout=10 $host exit
        and echo $host
    end
end
