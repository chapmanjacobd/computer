# Defined interactively
function tmux.cb
    tmux capture-pane -pS- | cb
end
