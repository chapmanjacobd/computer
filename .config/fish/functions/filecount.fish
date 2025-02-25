# Defined interactively
function filecount
    fd -tf . $argv | count
end
