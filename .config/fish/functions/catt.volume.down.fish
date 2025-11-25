# Defined interactively
function catt.volume.down
    if pgrep -f 'catt '; or catt status | grep 'State: PLAYING'
        catt volumedown 3
    else
        vol -3
    end
end
