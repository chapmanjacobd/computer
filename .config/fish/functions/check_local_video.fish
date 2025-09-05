# Defined interactively
function check_local_video
    echo $argv
    lb playlists ~/lb/torrents.db -s "$argv" -p --cols title,size 2>/dev/null

    set hosts (connectable-ssh backup pakon r730xd)
    locate_remote_mv.py -v -E /sync/ -E /archive/ --flex --hosts $hosts -- /video/ $argv
    print $hosts | parallel sshpc {} lb torrents -- $argv
end
