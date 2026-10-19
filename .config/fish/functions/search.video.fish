# Defined interactively
function search.video
    echo $argv
    lb database playlists ~/lb/torrents.db -s "$argv" -p --cols title,size 2>/dev/null

    set hosts (servers.ssh.connectable $servers_local)
    locate.remote.mv -v -E /sync/ -E /archive/ --flex --hosts $hosts -- /video/ $argv
    print $hosts | parallel server.ssh {} lb torrent info -- $argv

    xsql $argv
end
