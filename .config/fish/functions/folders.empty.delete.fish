# Defined interactively
function folders.empty.delete
    string length -q -- $argv; and $argv
    find . -type d -empty -delete
end
