# The sound I can hear: a peer casting, else whatever this machine is playing.
# catt.volume.up is the leaf, so local playback keeps using pactl/termux-volume.
function volup
    set -l owner (lt.owner)
    if test -n "$owner"; and test "$owner" != (hostname)
        lt.at volup
    else
        catt.volume.up
    end
end
