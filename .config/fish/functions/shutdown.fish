# Defined interactively
function shutdown
    progress -wc ffmpeg | grep -v 'No such command'
    if test $status -ne 0
        # sudo ethtool -s enp3s0 wol g
        sudo shutdown now
    end
end
