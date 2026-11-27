# Defined interactively
function file.handlers --wraps='lsof'
    lsof -n -t $argv
end
