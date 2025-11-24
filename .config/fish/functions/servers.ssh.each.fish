# Defined interactively
function servers.ssh.each
    for pc in $servers
        sshpc $pc -t $argv
    end
end
