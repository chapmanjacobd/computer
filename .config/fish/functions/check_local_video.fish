# Defined interactively
function check_local_video
    echo $argv
    lb playlists ~/lb/torrents.db -s "$argv" -p --cols title,size 2>/dev/null

    set hosts (connectable-ssh $servers_local)
    locate_remote_mv.py -v -E /sync/ -E /archive/ --flex --hosts $hosts -- /video/ $argv
    print $hosts | parallel server.ssh {} lb torrents -- $argv

    xsql $argv
end
