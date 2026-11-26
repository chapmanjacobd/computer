if not functions -q _worktree_ensure
    source $__fish_config_dir/functions/_worktree_helpers.fish
end

function zg --argument-names query --description 'Jump to or create a worktree for a branch in the current repository'
    if test (count $argv) -gt 1
        echo 'zg: too many arguments' >&2
        return 2
    end

    set -l repo (_worktree_repo_root (pwd))
    if test -z "$repo"
        echo 'zg: not inside a git repository' >&2
        return 1
    end

    if test "$query" = -
        git switch -
        return
    end

    # An exact worktree, local branch, or remote branch name jumps straight
    # there. Partial matches go through fzf, and typed non-matches can create a
    # new branch.
    set -l branch
    if test -n "$query"
        for row in (_worktree_branch_rows "$repo")
            set -l parts (string split \t -- $row)
            if test "$parts[1]" = "$query"
                set branch $parts[1]
                break
            else if test "$parts[2]" = remote; and test "$parts[3]" = "$query"
                set branch $parts[1]
                break
            end
        end
    end

    if test -z "$branch"
        set branch (_worktree_pick_branch "$repo" "$query")
        or return 0
    end

    _worktree_ensure "$repo" "$branch"
end
