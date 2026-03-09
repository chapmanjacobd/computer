# Defined via `source`
function gw.merge --argument-names target
    set -l cwd (pwd)
    set -l git_dir (git rev-parse --git-dir)
    
    # Check if we're in a worktree (worktrees have .git as a file, not a directory)
    set -l is_worktree 0
    if test -f "$cwd/.git"
        set is_worktree 1
    end
    
    # Get main repo path from worktree's .git file
    set -l main_repo ""
    if test $is_worktree -eq 1
        set -l git_file (cat "$cwd/.git")
        set -l gitdir_path (string trim (string replace 'gitdir: ' '' $git_file))
        # gitdir points to <main-repo>/.git/worktrees/<name>, go back to main repo
        set main_repo (dirname (dirname (dirname $gitdir_path)))
    else
        set main_repo (git rev-parse --show-toplevel)
    end

    # --- if inside worktree ---
    if test $is_worktree -eq 1
        set -l branch (git branch --show-current)
        set -l target_path $cwd

        if not git diff-index --quiet HEAD --
            git add .
            git commit -m "Complete work on $branch"
        else
            echo "No changes to commit."
        end

        cd $main_repo
        git merge $branch
        git worktree remove $target_path
        return
    end

    # --- gather worktrees (excluding main repo) ---
    set -l branches
    set -l paths

    for line in (git worktree list --porcelain)
        if string match -q 'worktree *' $line
            set -a paths (string trim (string replace 'worktree ' '' $line))
        else if string match -q 'branch *' $line
            set -a branches (string replace 'refs/heads/' '' (string trim (string replace 'branch ' '' $line)))
        end
    end

    # Filter out the main repo (first entry)
    set -l filtered_branches
    set -l filtered_paths
    for i in (seq (count $branches))
        if test "$paths[$i]" != "$main_repo"
            set -a filtered_branches $branches[$i]
            set -a filtered_paths $paths[$i]
        end
    end
    set branches $filtered_branches
    set paths $filtered_paths

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
        set -l sel (for i in (seq (count $branches)); printf "%s\t%s\n" $branches[$i] $paths[$i]; end | fzf --select-1)
        set chosen_branch (string split \t $sel)[1]
        set target_path (string split \t $sel)[2]
    end

    git merge "$chosen_branch"
    git commit

    git worktree remove $target_path
end
