# Defined interactively
function torrents
    parallel sshpc {} lb torrents $argv ::: (connectable-ssh $servers)
end
