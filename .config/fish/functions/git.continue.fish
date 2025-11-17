# Defined interactively
function git.continue
    git cherry-pick --continue
    or git rebase --continue
    or git merge --continue
end
