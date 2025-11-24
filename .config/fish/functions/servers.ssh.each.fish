# Defined interactively
function servers.ssh.each
    for pc in $servers
        server.ssh $pc -t $argv
    end
end
