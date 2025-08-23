# Defined interactively
function referer
    awk -F'"' '{print $4}'
end
