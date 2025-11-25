# Defined interactively
function ssh.speedtest
    yes | pv | ssh $argv "cat >/dev/null"
end
