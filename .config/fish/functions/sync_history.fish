# Defined interactively
function sync_history
    cat ~/.local/share/fish/fish_history.sync-conflict-* >>~/.local/share/fish/fish_history
    trash-put ~/.local/share/fish/fish_history.sync-conflict-*

    cat ~/.local/share/z/data.sync-conflict* >>~/.local/share/z/data
    trash-put ~/.local/share/z/data.sync-conflict*
end
