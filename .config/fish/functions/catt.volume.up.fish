# Defined interactively
function catt.volume.up
    if pgrep -f 'catt '; or catt -d (lt.device) status | grep 'State: PLAYING'
        catt -d (lt.device) volumeup 2
    else
        vol +2
    end
end
