function voldown
    set -l owner (lt.owner)
    if test -n "$owner"; and test "$owner" != (hostname)
        lt.at voldown
    else
        catt.volume.down
    end
end
