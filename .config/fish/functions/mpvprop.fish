# Defined interactively
function mpvprop
    mpvcmd '{ "command": ["get_property", "'$argv'"] }'
end
