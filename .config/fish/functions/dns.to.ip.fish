# Defined interactively
function dns.to.ip
    dig +short $argv | sed "/[^0-9\.]/d"
end
