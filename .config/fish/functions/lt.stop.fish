# Defined interactively
function lt.stop
    if pgrep -f 'lb listen'; or pgrep -f 'lb lt'
        lb stop
    else
        ssh pakon lb stop
    end
end
