# Defined interactively
function sync_history
    cat ~/.local/share/fish/fish_history.sync-conflict-* >>~/.local/share/fish/fish_history
    trash-put ~/.local/share/fish/fish_history.sync-conflict-*
end
