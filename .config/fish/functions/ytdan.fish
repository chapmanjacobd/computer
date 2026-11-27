# Defined interactively
function ytdan --wraps='yta'
    cd (d dump/audio/music/)
    yta --reject-title '' $argv
end
