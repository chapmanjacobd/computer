# Defined interactively
function git.continue
    # An incremental merge keeps its state under refs/imerge. Continue it, and
    # finish it once the last pairwise conflict has been resolved.
    if test -n "$(git for-each-ref --count=1 refs/imerge)"
        git-imerge continue
        or return

        # A pending conflict leaves the working tree dirty. A clean tree means
        # the last conflict is recorded, so finish the merge onto the branch.
        if git diff --quiet; and git diff --cached --quiet
            git-imerge finish
            or return
        end
        return 0
    end

    git cherry-pick --continue
    or git rebase --continue
    or git merge --continue
end
