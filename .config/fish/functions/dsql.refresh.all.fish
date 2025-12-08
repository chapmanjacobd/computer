# Defined interactively
function dsql.refresh.all
    for s in (blockdevices.py --mountpoints | grep -v /boot)
        dsql.refresh $s
    end
end
