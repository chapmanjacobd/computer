# Defined interactively
function domain.ip --wraps='dig'
    dig +short $argv | tail -n1
end
