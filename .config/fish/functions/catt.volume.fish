# Defined interactively
function catt.volume
    if pgrep -f catt
        catt volume $argv
    else
        vol $argv
    end
end
