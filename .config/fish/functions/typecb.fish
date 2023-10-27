# Defined interactively
function typecb
    sleep 1
    xdotool type (xsel -bo | tr \\n \\r | sed s/\\r\*\$// | string collect)
end
