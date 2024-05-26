# Defined interactively
function mpvset
    mpvcmd '{ "command": ["set_property", "'$argv[1]'", "'$argv[2]'"] }'
end
