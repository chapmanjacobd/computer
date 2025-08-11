# Defined interactively
function wget.single
    timeout 5m wget2 --user-agent="$(useragent)" --span-hosts "$argv"
end
