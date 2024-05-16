# Defined interactively
function presume-fzf
    presume (ppaused | fzf-choose | cut -d' ' -f1)
end
