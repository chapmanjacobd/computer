# Defined interactively
function confirm.yes
    read -P "$argv> " response
    not contains $response n N no NO
end
