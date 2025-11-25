# Defined interactively
function lines.duplicates
    sort | uniq -c | awk '$1 > 1 { print $2, $1 }'
end
