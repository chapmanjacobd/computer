# Defined interactively
function speedtest
    yes | pv | ssh $argv "cat >/dev/null"
end
