# Defined interactively
function access_log_ua
    awk -F'"' '{print $6}'
end
