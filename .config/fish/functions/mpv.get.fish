# Defined interactively
function mpv.get
    mpv.cmd '{ "command": ["get_property", "'$argv'"] }'
end
