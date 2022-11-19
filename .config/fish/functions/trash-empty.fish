# Defined interactively
function trash-empty
    trash-list | tee -a ~/.local/share/trashed.txt
    command trash-empty $argv
    sort --unique --ignore-case ~/.local/share/trashed.txt | sponge ~/.local/share/trashed.txt
end
