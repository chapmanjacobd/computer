# Defined interactively
function check_local_video
    echo $argv
    lb playlists ~/lb/torrents.db -s $argv -p --cols title,size 2>/dev/null
    locate_remote_mv.py -v -E /sync/ -E /archive/ --flex --hosts backup pakon r730xd -- /video/ $argv
    print pakon backup r730xd | parallel sshpc {} lb torrents -- $argv
end
