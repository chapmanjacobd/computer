# Defined interactively
function g.merge --description 'Commit, merge, and prune a managed git worktree'
    argparse 'b/branch=' 'm/message=' -- $argv
    set -l args $argv

    # Configuration
    set -l wt_root "$HOME/.git-worktrees"

    # Parameter setup
    if not set -q _flag_branch
        set _flag_branch $args[1]
    end

    set -l target_path "$wt_root/$_flag_branch"

    if not test -d "$target_path"
        echo "Error: Worktree for '$_flag_branch' not found in $wt_root"
        return 1
    end

    # 1. Enter worktree and commit
    cd $target_path

    # Check for changes
    if not git diff-index --quiet HEAD --
        set -l commit_msg $_flag_message
        if not set -q _flag_message
            set commit_msg "Complete work on $_flag_branch"
        end

        git add .
        git commit -m "$commit_msg"
    else
        echo "No changes to commit."
    end

    # 2. Return to main and merge
    cd - # Back to where you started
    echo "Merging '$_flag_branch' into current branch..."
    git merge $_flag_branch

    # 3. Prune the worktree
    git worktree remove $target_path

    # Cleanup branch if desired (optional)
    # git branch -d $_flag_branch
end
