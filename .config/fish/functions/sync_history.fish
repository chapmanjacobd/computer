# Defined interactively
function sync_history
    count ~/.local/share/fish/fish_history.sync-conflict-* >/dev/null; and cat ~/.local/share/fish/fish_history.sync-conflict-* >>~/.local/share/fish/fish_history
    count ~/.local/share/fish/fish_history.sync-conflict-* >/dev/null; and trash-put ~/.local/share/fish/fish_history.sync-conflict-*

    cp ~/.local/share/fish/fish_history ~/d/00_Metadata/SECURE/

    count ~/.local/share/z/data.sync-conflict* >/dev/null; and cat ~/.local/share/z/data.sync-conflict* >>~/.local/share/z/data
    count ~/.local/share/z/data.sync-conflict* >/dev/null; and trash-put ~/.local/share/z/data.sync-conflict*
end
