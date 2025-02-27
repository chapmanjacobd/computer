# Defined interactively
function check_local
    echo $argv
    lb playlists ~/lb/torrents.db -s $argv -pf --cols title | lb rs
    locate_remote_mv.py -v --flex --hosts backup pakon r730xd -- $argv
    echon pakon backup r730xd | parallel sshpc {} lb torrents -- $argv
end
