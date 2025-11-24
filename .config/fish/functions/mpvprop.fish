# Defined interactively
function mpvprop
    mpv.cmd '{ "command": ["get_property", "'$argv'"] }'
end
