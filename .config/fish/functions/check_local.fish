# Defined interactively
function check_local
    echo $argv
    locate_remote_mv.py -v --flex --hosts backup pakon r730xd -- $argv
    echon pakon backup r730xd | parallel sshpc {} lb torrents -- $argv
end
