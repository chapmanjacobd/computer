# Defined interactively
function rebase-reword
    git rebase -i (git rev-list --max-parents=0 HEAD)^ --exec 'git reset --soft HEAD^ && git commit -m "$(wip_message.py)"'
end
