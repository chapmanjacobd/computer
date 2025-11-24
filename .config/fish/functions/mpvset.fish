# Defined interactively
function mpvset
    mpv.cmd '{ "command": ["set_property", "'$argv[1]'", "'$argv[2]'"] }'
end
