# Defined via `source`
function hhmmss
    set seconds $argv[1]

    set hours (math "$seconds / 3600" | sed 's/\..*//')
    set minutes (math "($seconds / 60) % 60" | sed 's/\..*//')
    set remaining_seconds (math "$seconds % 60" | sed 's/\..*//')

    if test $hours -gt 0
        printf "%02d:%02d:%02d\n" $hours $minutes $remaining_seconds
    else
        printf "%02d:%02d\n" $minutes $remaining_seconds
    end
end
