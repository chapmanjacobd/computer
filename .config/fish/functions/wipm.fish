# Defined interactively
function wipm
    git add .

    # 1. Freeze staged state into an immutable Git tree object (O(1) SHA)
    set -l tree_oid (git write-tree)
    set -l parent_oid (git rev-parse HEAD)

    # 2. Inspect against the frozen tree rather than current index/disk
    git --no-pager diff $parent_oid $tree_oid
    git diff --stat $parent_oid $tree_oid

    if gum confirm --default=no
        # 3. Create commit object pointing directly to frozen tree
        set -l commit_oid (git commit-tree $tree_oid -p $parent_oid -S -m "$argv")

        # 4. Atomically advance HEAD/branch to new commit (validating parent didn't move)
        git update-ref HEAD $commit_oid $parent_oid
        git pull
        git push
    else
        return 1
    end
end
