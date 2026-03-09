# Defined via `source`
function gw.merge --argument-names target
    set -l main_repo (git rev-parse --show-toplevel)
    set -l cwd (pwd)

    # --- if inside worktree ---
    if test "$cwd" != "$main_repo"
        set -l branch (git branch --show-current)
        set -l target_path $cwd

        if not git diff-index --quiet HEAD --
            git add .
            git commit -m "Complete work on $branch"
        else
            echo "No changes to commit."
        end

        cd $main_repo
        echo "Squash merging '$branch'..."
        git merge --squash $branch
        git commit -m "Merge $branch (squash)"

        git worktree remove $target_path
        return
    end

    # --- gather worktrees ---
    set -l branches
    set -l paths

    git worktree list --porcelain | while read -l line
        switch $line
            case 'worktree *'
                set paths $paths (string split ' ' $line)[2]
            case 'branch *'
                set branches $branches (string replace 'refs/heads/' '' (string split ' ' $line)[2])
        end
    end

    # --- resolve target ---
    set -l chosen_branch
    set -l target_path

    if test -n "$target"
        for i in (seq (count $branches))
            if test "$branches[$i]" = "$target" -o (basename $paths[$i]) = "$target" -o "$paths[$i]" = "$target"
                set chosen_branch $branches[$i]
                set target_path $paths[$i]
                break
            end
        end
        if test -z "$chosen_branch"
            echo "No matching worktree: $target"
            return 1
        end
    else
        set -l sel (printf "%s\t%s\n" $branches $paths | fzf)
        set chosen_branch (string split \t $sel)[1]
        set target_path (string split \t $sel)[2]
    end

    git merge "$chosen_branch"
    git commit

    git worktree remove $target_path
end
