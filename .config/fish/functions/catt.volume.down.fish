# Defined interactively
function catt.volume.down
    if pgrep -f 'catt '; or catt status | grep 'State: PLAYING'
        catt volume.down 3
    else
        vol -3
    end
end
