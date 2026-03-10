# Defined interactively
function git.pop --argument-names branch commit
    set commit (test -n "$commit"; and echo $commit; or echo HEAD)

    # derive branch name from commit message if not provided
    if test -z "$branch"
        set msg (git log -1 --pretty=%s $commit)
        set branch (string lower $msg | string replace -ra '[^a-z0-9]+' '-' | string trim -c '-')
    end

    # prevent overwrite
    if git show-ref --verify --quiet refs/heads/$branch
        echo "branch already exists: $branch" >&2
        return 1
    end

    git switch -c $branch $commit
    or return

    git switch -
    or return

    git reset --keep "$commit^"
end
