# Defined interactively
function lt-stop
    if pgrep -f 'lb listen'
        lb stop
    else
        ssh pakon lb stop
    end
end
