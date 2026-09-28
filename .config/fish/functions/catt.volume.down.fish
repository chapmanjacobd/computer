# Defined interactively
function catt.volume.down
    if pgrep -f 'catt '; or catt -d (lt.device) status | grep 'State: PLAYING'
        catt -d (lt.device) volumedown 3
    else
        vol -3
    end
end
