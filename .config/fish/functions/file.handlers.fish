# Defined interactively
function file.handlers
    lsof -n -t $argv
end
