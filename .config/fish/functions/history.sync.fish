# Defined interactively
function history.sync
    history merge

    count ~/.local/share/fish/fish_history.sync-conflict-* >/dev/null; and cat ~/.local/share/fish/fish_history.sync-conflict-* >>~/.local/share/fish/fish_history
    count ~/.local/share/fish/fish_history.sync-conflict-* >/dev/null; and trash ~/.local/share/fish/fish_history.sync-conflict-*

    cp ~/.local/share/fish/fish_history ~/sync/self/secure/
    count ~/sync/self/secure/fish_history.sync-conflict-* >/dev/null; and trash ~/sync/self/secure/fish_history.sync-conflict-*

    history merge

    # copyq ?
    # fd -HI sync-conflict -x rm
end
