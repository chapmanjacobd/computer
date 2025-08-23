# Defined interactively
function rebase-reword
    git rebase -i (git rev-list --max-parents=0 HEAD)^ --exec 'git commit --amend -m "$(wip_message.py HEAD^)"'
end
