# Defined interactively
function sqlite-views
    sqlite-utils views --tsv $argv | tail -n +2 | strip_quotes
end
