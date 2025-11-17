# Defined interactively
function git.abort
    git cherry-pick --abort
    or git rebase --abort
    or git merge --abort
end
