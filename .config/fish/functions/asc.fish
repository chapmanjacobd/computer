# Defined interactively
function asc --wraps='sort'
    sort | uniq -c | sort -g $argv
end
