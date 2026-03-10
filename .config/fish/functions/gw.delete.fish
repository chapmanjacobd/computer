# Defined via `source`
function gw.delete
    set -l common_dir (git rev-parse --git-common-dir 2>/dev/null)

    # Check if we are in the main repo or a worktree
    if test "$common_dir" = ".git" -o "$common_dir" = "."
        # Show multi-select with a status preview for each worktree
        set -l selections (git worktree list --porcelain | string match -r "worktree .*" | string replace "worktree " "" | \
                            fzf --multi \
                                --header "TAB to multi-select | ENTER to delete" \
                                --preview 'git -C {} status -sb; echo "---"; git -C {} diff --stat')

        for path in $selections
            if test "$path" != (pwd)
                git worktree remove --force "$path"
                echo "Nuked: $path"
            else
                echo "Skipped: Cannot delete current directory ($path)"
            end
        end
    else
        # Currently inside a worktree: jump home and kill this one
        set -l worktree_path (pwd)
        set -l main_abs (realpath "$common_dir/..")

        cd "$main_abs"
        git worktree remove --force "$worktree_path"
    end
end
