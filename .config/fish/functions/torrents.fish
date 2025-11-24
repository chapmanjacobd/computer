# Defined interactively
function torrents
    parallel server.ssh {} lb torrents $argv ::: (connectable-ssh $servers)
end
