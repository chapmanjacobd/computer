# Defined interactively
function line --wraps='head'
    head -n "$argv" | tail -n 1
end
