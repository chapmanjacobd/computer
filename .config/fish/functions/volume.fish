# Defined interactively
function volume
if pgrep -f catt
catt volume $argv
else
vol $argv
end
end
