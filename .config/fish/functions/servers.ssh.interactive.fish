# Defined interactively
function servers.ssh.interactive
    for pc in $servers
        ssh -t $pc $argv
    end
end
