# Defined in /home/xk/.config/fish/functions/g.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function gw -a branch
    set -l wt_root "$HOME/.git-worktrees"
    mkdir -p $wt_root

    set -l target_path "$wt_root/$branch"

    git worktree add -b $branch $target_path (git main)

    cd $target_path
end
