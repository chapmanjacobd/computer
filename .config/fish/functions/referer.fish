# Defined interactively
function referer
    awk '{print $11}' | sed 's|"||g'
end
