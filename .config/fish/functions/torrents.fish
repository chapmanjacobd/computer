# Defined interactively
function torrents
    parallel server.ssh {} lb torrent info $argv ::: (servers.ssh.connectable $servers)
end
