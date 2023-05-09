# Defined interactively
function ffsmall_delete
    ffsmall $argv
    and trash-put "$argv[1]"
end
