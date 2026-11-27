# Defined interactively
function untimestamp --wraps='date'
    date -d @$argv
end
