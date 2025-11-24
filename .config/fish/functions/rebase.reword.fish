# Defined interactively
function rebase.reword
    git -c rebase.instructionFormat='%s%nexec GIT_COMMITTER_DATE="%cD" GIT_AUTHOR_DATE="%aD" git commit --amend --no-edit --reset-author' rebase -i (git log --reverse --pretty=%H | sed -n '2p') --exec 'git commit --amend --no-edit --reset-author -m "$(wip_message.py HEAD)"'
end
