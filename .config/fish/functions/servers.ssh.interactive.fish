# Defined interactively
function servers.ssh.interactive --wraps='ssh'
    for pc in $servers
        ssh -t $pc $argv
    end
end
