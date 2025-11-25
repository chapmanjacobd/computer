# Defined interactively
function mpv.set
    mpv.cmd '{ "command": ["set_property", "'$argv[1]'", "'$argv[2]'"] }'
end
