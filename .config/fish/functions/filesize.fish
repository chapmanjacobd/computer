# Defined interactively
function filesize
    du -bc $argv | tail -n 1 | cut -f1
end
