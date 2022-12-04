# Defined interactively
function nextSongDelete
    if pgrep -f 'lb lt'
        lb next --delete
    else
        ssh pakon lb next --delete
    end
end
