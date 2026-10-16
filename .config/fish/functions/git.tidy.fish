function git.tidy --description "Prune remotes, delete merged branches, and run Git maintenance"
    set -l dry_run 0
    set -l skip_fetch 0
    set -l assume_yes 0
    set -l target

    for arg in $argv
        switch $arg
            case --dry-run
                set dry_run 1
            case --no-fetch
                set skip_fetch 1
            case --yes -y
                set assume_yes 1
            case '-*'
                echo "git.tidy: unknown option: $arg" >&2
                return 2
            case '*'
                if test -n "$target"
                    echo "git.tidy: expected at most one merge target" >&2
                    return 2
                end
                set target $arg
        end
    end

    set -l in_worktree (git rev-parse --is-inside-work-tree 2>/dev/null)
    if test "$in_worktree" != true
        echo "git.tidy: run this inside a Git worktree" >&2
        return 1
    end

    if test $dry_run -eq 1
        echo "dry run: skipping fetch and maintenance commands"
    else if test $skip_fetch -eq 0
        echo "Fetching remotes and pruning stale remote-tracking branches..."
        if not git fetch --all --prune
            echo "git.tidy: fetch failed; refusing to delete branches" >&2
            return 1
        end
    end

    if test -z "$target"
        set -l remotes (git remote)
        set -l remote $remotes[1]

        if test -n "$remote"
            set target (git symbolic-ref --quiet --short "refs/remotes/$remote/HEAD" 2>/dev/null)

            if test -z "$target"
                for candidate in main master
                    if git show-ref --verify --quiet "refs/remotes/$remote/$candidate"
                        set target "$remote/$candidate"
                        break
                    end
                end
            end
        end
    else
        set target (string replace -r '^refs/remotes/' '' -- "$target")
    end

    set -l maintenance_status 0
    set -l current_branch (git symbolic-ref --quiet --short HEAD 2>/dev/null)
    set -l deletable_branches

    if test -n "$target"
        if not git rev-parse --verify --quiet "$target^{commit}" >/dev/null 2>&1
            echo "git.tidy: merge target does not resolve: $target" >&2
            return 1
        end

        set -l target_parts (string split -m 1 / -- "$target")
        set -l protected_branch $target
        if test (count $target_parts) -gt 1
            set protected_branch $target_parts[2]
        end

        set -l worktree_branches
        for line in (git worktree list --porcelain 2>/dev/null)
            if string match -q 'branch refs/heads/*' -- "$line"
                set -a worktree_branches (string replace 'branch refs/heads/' '' -- "$line")
            end
        end

        set -l merged_branches (git branch --merged "$target" --format='%(refname:short)' 2>/dev/null)
        if test $status -ne 0
            echo "git.tidy: could not list branches merged into $target" >&2
            return 1
        end

        for branch in $merged_branches
            if test "$branch" = "$current_branch"; or \
                    test "$branch" = "$protected_branch"; or \
                    contains -- "$branch" $worktree_branches
                continue
            end
            set -a deletable_branches "$branch"
        end

        echo "Merge target: $target"
        if test (count $deletable_branches) -gt 0
            echo "Local branches merged into $target:"
            for branch in $deletable_branches
                echo "  $branch"
            end

            if test $dry_run -eq 1
                echo "dry run: would delete (with verified merged history) the branches above"
            else if test $assume_yes -eq 1; or confirm "Delete these branches"
                for branch in $deletable_branches
                    if not git branch -D -- "$branch"
                        set maintenance_status 1
                    end
                end
            else
                echo "Skipped local branch deletion."
            end
        else
            echo "No deletable local branches merged into $target."
        end
    else
        echo "No remote default branch found; skipping merged local branch cleanup."
    end

    if test $dry_run -eq 1
        echo "dry run: would prune stale worktree metadata and run git gc"
        return $maintenance_status
    end

    echo "Pruning stale worktree metadata..."
    if not git worktree prune
        set maintenance_status 1
    end

    echo "Running git gc..."
    if not git gc
        set maintenance_status 1
    end

    return $maintenance_status
end
