# Defined interactively
function folders.empty.delete
    $argv
    find . -type d -empty -delete
end
