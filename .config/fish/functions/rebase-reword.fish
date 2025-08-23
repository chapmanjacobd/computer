# Defined interactively
function rebase-reword
    git rebase -i (git log --reverse --pretty=%H | sed -n '2p') --exec 'git commit --amend -m "$(wip_message.py HEAD)"'
end
