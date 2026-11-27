# Defined via `source`
function domain.ip.org --wraps='whois'
    whois $(domain.ip $argv) | grep -iE "orgname|organization|descr"
end
