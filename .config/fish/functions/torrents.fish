# Defined interactively
function torrents --wraps='parallel'
    parallel server.ssh {} lb torrent info $argv ::: (servers.ssh.connectable $servers)
end
