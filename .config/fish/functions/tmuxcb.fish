# Defined interactively
function tmuxcb
    tmux capture-pane -pS- | cb
end
