# Defined interactively
function fileTypeStatistics
    fd -tf -HI . $argv | ext | asc
end
