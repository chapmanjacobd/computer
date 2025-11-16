# Defined interactively
function check_local
    echo $argv
    lb playlists ~/lb/torrents.db -s "$argv" -pf --cols title 2>/dev/null | lb rs 2>/dev/null

    set hosts (connectable-ssh $servers_local)
    locate_remote_mv.py -v --flex --hosts $hosts -- $argv
    print $hosts | parallel sshpc {} lb torrents -- $argv

    xsql $argv
end
