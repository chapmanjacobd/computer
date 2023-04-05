# Defined interactively
function sqlite-tables
    sqlite-utils tables --tsv $argv | tail -n +2
end
