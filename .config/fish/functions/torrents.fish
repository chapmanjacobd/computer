# Defined interactively
function torrents
    parallel server.ssh {} lb torrents $argv ::: (servers.ssh.connectable $servers)
end
