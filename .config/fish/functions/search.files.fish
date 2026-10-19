# Defined interactively
function search.files
    echo $argv
    lb database playlists ~/lb/torrents.db -s "$argv" -pf --cols title 2>/dev/null | lb text sort regex 2>/dev/null

    set hosts (servers.ssh.connectable $servers_local)
    locate.remote.mv -v --flex --hosts $hosts -- $argv
    print $hosts | parallel server.ssh {} lb torrent info -- $argv

    xsql $argv
end
