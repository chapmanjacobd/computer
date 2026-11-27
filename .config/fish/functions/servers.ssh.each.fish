# Defined interactively
function servers.ssh.each --wraps='server.ssh'
    for pc in $servers
        server.ssh $pc -t $argv
    end
end
