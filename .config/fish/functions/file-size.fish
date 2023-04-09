# Defined interactively
function file-size
    du -c $argv | tail -n 1 | cut -f1
end
