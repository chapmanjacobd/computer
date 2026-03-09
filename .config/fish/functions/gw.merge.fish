# Defined interactively
function gw.merge --argument-names target
    set -l wt_root "$HOME/.git-worktrees"

    # detect if inside a worktree
    set -l wt_path (git rev-parse --git-path worktrees 2>/dev/null)

    if test -n "$wt_path"
        # --- inside worktree ---
        set -l branch (git branch --show-current)
        set -l target_path (pwd)

        # commit if needed
        if not git diff-index --quiet HEAD --
            git add .
            git commit -m "Complete work on $branch"
        else
            echo "No changes to commit."
        end

        # return to main repo
        set -l main_repo (git rev-parse --show-toplevel)
        cd $main_repo

        echo "Squash merging '$branch'..."
        git merge --squash $branch
        git commit -m "Merge $branch (squash)"

        git worktree remove $target_path
        return
    end

    # --- in main repo ---
    set -l worktrees (git worktree list --porcelain)
    set -l branches
    set -l paths

    for line in $worktrees
        if string match -q 'worktree *' $line
            set paths $paths (string split ' ' $line)[2]
        else if string match -q 'branch *' $line
            set branches $branches (string replace 'refs/heads/' '' (string split ' ' $line)[2])
        end
    end

    set -l chosen_branch
    set -l target_path

    if set -q target[1]
        # try branch match
        for i in (seq (count $branches))
            if test "$branches[$i]" = "$target"
                set chosen_branch $branches[$i]
                set target_path $paths[$i]
                break
            end
        end

        # try path / folder name
        if test -z "$chosen_branch"
            for i in (seq (count $paths))
                if test (basename $paths[$i]) = "$target" -o "$paths[$i]" = "$target"
                    set chosen_branch $branches[$i]
                    set target_path $paths[$i]
                    break
                end
            end
        end

        if test -z "$chosen_branch"
            echo "No matching worktree for '$target'"
            return 1
        end
    else
        set -l selection (printf "%s\t%s\n" $branches $paths | fzf)
        set chosen_branch (string split \t $selection)[1]
        set target_path (string split \t $selection)[2]
    end

    if test -z "$chosen_branch"
        echo "No worktree selected."
        return 1
    end

    echo "Merging '$chosen_branch'..."
    git merge --squash $chosen_branch
    git commit -m "Merge $chosen_branch (squash)"

    git worktree remove $target_path
end
