# Defined interactively
function zg --argument-names branch
    if test "$branch" = -
        git switch -
        return
    end

    set -l selection (git branch --format='%(refname:short)' | fzf --query "$branch" --select-1 --exit-0)

    if test -n "$selection"
        # Check if the branch is active in any worktree
        set -l worktree_path (git worktree list --porcelain | string match -r "worktree .*" | string replace "worktree " "" | while read -l path
                if test (git -C "$path" branch --show-current) = "$selection"
                    echo "$path"
                    break
                end
            end)

        if test -n "$worktree_path"
            cd "$worktree_path"
        else
            git switch "$selection"
        end
    end
end
