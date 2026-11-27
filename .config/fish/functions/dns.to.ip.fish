# Defined interactively
function dns.to.ip --wraps='dig'
    dig +short $argv | sed "/[^0-9\.]/d"
end
