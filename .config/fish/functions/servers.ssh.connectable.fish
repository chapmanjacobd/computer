# Defined interactively
function servers.ssh.connectable
    for host in $argv
        ssh -o ConnectTimeout=10 $host exit
        and echo $host
    end
end
