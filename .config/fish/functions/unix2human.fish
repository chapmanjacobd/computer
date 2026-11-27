# Defined interactively
function unix2human --wraps='date'
    date -d @$argv
end
