# Defined interactively
function catt.volume.up
    if pgrep -f 'catt '; or catt status | grep 'State: PLAYING'
        catt volumeup 2
    else
        vol +2
    end
end
