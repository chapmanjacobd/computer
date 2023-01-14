# Defined interactively
function nextSongDelete
    if pgrep -f 'lb listen'
        lb next --delete
    else
        ssh pakon lb next --delete
    end
end
