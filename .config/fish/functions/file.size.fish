# Defined interactively
function file.size --wraps='du'
    du -bc $argv | tail -n 1 | cut -f1
end
