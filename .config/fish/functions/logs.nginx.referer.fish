# Defined interactively
function logs.nginx.referer
    awk -F'"' '{print $4}'
end
