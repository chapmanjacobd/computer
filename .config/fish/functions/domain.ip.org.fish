# Defined via `source`
function domain.ip.org
    whois $(domain.ip $argv) | grep -iE "orgname|organization|descr"
end
