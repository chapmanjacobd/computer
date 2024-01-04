# Defined interactively
function sync_history
    count ~/.local/share/fish/fish_history.sync-conflict-* >/dev/null; and cat ~/.local/share/fish/fish_history.sync-conflict-* >>~/.local/share/fish/fish_history
    count ~/.local/share/fish/fish_history.sync-conflict-* >/dev/null; and trash-put ~/.local/share/fish/fish_history.sync-conflict-*

    cp ~/.local/share/fish/fish_history ~/d/sync/self/secure/
    count ~/d/sync/self/secure/fish_history.sync-conflict-* >/dev/null; and trash-put ~/d/sync/self/secure/fish_history.sync-conflict-*

    # copyq ?
    # fd -HI sync-conflict -x rm
end
