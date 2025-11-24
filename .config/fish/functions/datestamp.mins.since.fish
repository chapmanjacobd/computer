# Defined interactively
function datestamp.mins.since --argument mins_mark
    set current_mark (math -s 0 (date -d "1970-01-01 UTC $(date +%T)" +%s)'/60')
    math "$current_mark-$mins_mark"
end
