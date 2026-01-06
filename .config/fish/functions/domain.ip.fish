# Defined interactively
function domain.ip
    dig +short $argv | tail -n1
end
