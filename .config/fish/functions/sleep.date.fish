# Defined interactively
function sleep.date --argument target_date
    set current_date (date --iso-8601=seconds)

    set sleep_seconds (math (date -d "$target_date" +%s) - (date -d "$current_date" +%s))
    echo sleeping for $sleep_seconds
    sleep $sleep_seconds
end
