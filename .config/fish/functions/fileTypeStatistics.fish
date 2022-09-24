# Defined interactively
function fileTypeStatistics
    fd -tf . $argv | ext | asc
end
