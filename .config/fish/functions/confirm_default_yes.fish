# Defined interactively
function confirm_default_yes
    read -P "$argv> " response
    not contains $response n N no NO
end
